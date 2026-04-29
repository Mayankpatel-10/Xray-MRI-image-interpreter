import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import cv2
from PIL import Image
from tqdm import tqdm
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, models
from sklearn.metrics import classification_report, confusion_matrix
import warnings

warnings.filterwarnings("ignore")
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class MedicalImageDataset(Dataset):
    """Custom dataset class for medical images"""

    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.classes = sorted(os.listdir(data_dir))
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        self.images = []
        self.labels = []
        for class_name in self.classes:
            class_dir = os.path.join(data_dir, class_name)
            if os.path.isdir(class_dir):
                for img_name in os.listdir(class_dir):
                    if img_name.lower().endswith((".png", ".jpg", ".jpeg")):
                        self.images.append(os.path.join(class_dir, img_name))
                        self.labels.append(self.class_to_idx[class_name])

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        label = self.labels[idx]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label


class GPUMedicalClassifier:
    """GPU optimized medical image classifier"""

    def __init__(self, image_size=224, batch_size=32):
        self.image_size = image_size
        self.batch_size = batch_size
        self.device = device
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            if gpu_memory >= 8:
                self.batch_size = min(64, batch_size * 2)
            elif gpu_memory >= 4:
                self.batch_size = batch_size
            else:
                self.batch_size = min(16, batch_size)
        else:
            self.batch_size = min(16, batch_size)
        self.train_transform = transforms.Compose(
            [
                transforms.Resize((image_size, image_size)),
                transforms.RandomRotation(20),
                transforms.RandomHorizontalFlip(),
                transforms.RandomAffine(
                    degrees=0, translate=(0.2, 0.2), shear=0.2, scale=(0.8, 1.2)
                ),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )
        self.test_transform = transforms.Compose(
            [
                transforms.Resize((image_size, image_size)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )
        self.models = {}
        self.class_names = {}

    def create_model(self, num_classes):
        """Create model with transfer learning"""
        model = models.efficientnet_b0(
            weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1
        )
        num_ftrs = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(num_ftrs, num_classes)
        model = model.to(self.device)
        if torch.cuda.is_available():
            scaler = torch.cuda.amp.GradScaler()
        else:
            scaler = None
        return model, scaler

    def create_data_loaders(self, data_path, disease_type):
        """Create data loaders for training and testing"""
        if disease_type == "brain_tumor":
            train_dir = os.path.join(data_path, "brain_tumor", "Training")
            test_dir = os.path.join(data_path, "brain_tumor", "Testing")
        else:
            train_dir = os.path.join(data_path, "pnemonia", "train")
            test_dir = os.path.join(data_path, "pnemonia", "val")
        train_dataset = MedicalImageDataset(train_dir, transform=self.train_transform)
        test_dataset = MedicalImageDataset(test_dir, transform=self.test_transform)
        train_size = int(0.8 * len(train_dataset))
        val_size = len(train_dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            train_dataset, [train_size, val_size]
        )
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=2,
            pin_memory=True,
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=2,
            pin_memory=True,
        )
        test_loader = DataLoader(
            test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=2,
            pin_memory=True,
        )
        self.class_names[disease_type] = train_dataset.dataset.classes
        return train_loader, val_loader, test_loader

    def train_model(self, disease_type, epochs=20):
        """Train the model for a specific disease"""
        print(f"\nProcessing {disease_type.replace('_', ' ').title()} Detection")
        print("=" * 60)
        train_loader, val_loader, test_loader = self.create_data_loaders(
            "../Data", disease_type
        )
        num_classes = len(self.class_names[disease_type])
        print(f"Number of classes: {num_classes}")
        print(f"Class names: {self.class_names[disease_type]}")
        model, scaler = self.create_model(num_classes)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode="max", factor=0.5, patience=3
        )
        train_losses, val_losses = [], []
        train_accs, val_accs = [], []
        best_val_acc = 0.0
        for epoch in range(epochs):
            model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0
            train_pbar = tqdm(
                train_loader,
                desc=f"Epoch {epoch + 1}/{epochs} [Train]",
                leave=False,
                ncols=100,
                colour="green",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            )
            for batch_idx, (data, target) in enumerate(train_pbar):
                data, target = data.to(self.device), target.to(self.device)
                optimizer.zero_grad()
                if scaler:
                    with torch.cuda.amp.autocast():
                        output = model(data)
                        loss = criterion(output, target)
                    scaler.scale(loss).backward()
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    output = model(data)
                    loss = criterion(output, target)
                    loss.backward()
                    optimizer.step()
                train_loss += loss.item()
                _, predicted = torch.max(output.data, 1)
                train_total += target.size(0)
                train_correct += (predicted == target).sum().item()
                train_pbar.set_postfix({"loss": loss.item()})
            model.eval()
            val_loss = 0.0
            val_correct = 0
            val_total = 0
            with torch.no_grad():
                val_pbar = tqdm(
                    val_loader,
                    desc=f"Epoch {epoch + 1}/{epochs} [Val]",
                    leave=False,
                    ncols=100,
                    colour="blue",
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                )
                for data, target in val_pbar:
                    data, target = data.to(self.device), target.to(self.device)
                    if scaler:
                        with torch.cuda.amp.autocast():
                            output = model(data)
                            loss = criterion(output, target)
                    else:
                        output = model(data)
                        loss = criterion(output, target)
                    val_loss += loss.item()
                    _, predicted = torch.max(output.data, 1)
                    val_total += target.size(0)
                    val_correct += (predicted == target).sum().item()
            train_loss = train_loss / len(train_loader)
            val_loss = val_loss / len(val_loader)
            train_acc = 100 * train_correct / train_total
            val_acc = 100 * val_correct / val_total
            train_losses.append(train_loss)
            val_losses.append(val_loss)
            train_accs.append(train_acc)
            val_accs.append(val_acc)
            scheduler.step(val_acc)
            print(
                f"Epoch {epoch + 1}: Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%, "
                f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%"
            )
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save(model.state_dict(), f"best_{disease_type}_model.pth")
        self.models[disease_type] = model
        self.plot_training_history(
            disease_type, train_losses, val_losses, train_accs, val_accs
        )
        self.evaluate_model(disease_type, test_loader)
        return model, test_loader

    def plot_training_history(
        self, disease_type, train_losses, val_losses, train_accs, val_accs
    ):
        """Plot training history"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        ax1.plot(train_losses, label="Training Loss")
        ax1.plot(val_losses, label="Validation Loss")
        ax1.set_title(f"{disease_type.title()} - Model Loss")
        ax1.set_xlabel("Epoch")
        ax1.set_ylabel("Loss")
        ax1.legend()
        ax1.grid(True)
        ax2.plot(train_accs, label="Training Accuracy")
        ax2.plot(val_accs, label="Validation Accuracy")
        ax2.set_title(f"{disease_type.title()} - Model Accuracy")
        ax2.set_xlabel("Epoch")
        ax2.set_ylabel("Accuracy (%)")
        ax2.legend()
        ax2.grid(True)
        plt.show()

    def evaluate_model(self, disease_type, test_loader):
        """Evaluate model on test set"""
        model = self.models[disease_type]
        model.eval()
        all_predictions = []
        all_targets = []
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = model(data)
                _, predicted = torch.max(output, 1)
                all_predictions.extend(predicted.cpu().numpy())
                all_targets.extend(target.cpu().numpy())
        print(f"\n{disease_type.title()} - Test Results:")
        print(
            classification_report(
                all_targets,
                all_predictions,
                target_names=self.class_names[disease_type],
            )
        )
        cm = confusion_matrix(all_targets, all_predictions)
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=self.class_names[disease_type],
            yticklabels=self.class_names[disease_type],
        )
        plt.title(f"{disease_type.title()} - Confusion Matrix")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.show()

    def create_grad_cam(self, model, image_tensor, target_layer):
        """Create Grad-CAM visualization for PyTorch models"""
        try:
            target_layer = dict([*model.named_modules()])[target_layer]
            gradients = []
            activations = []

            def forward_hook(module, input, output):
                activations.append(output)

            def backward_hook(module, grad_input, grad_output):
                gradients.append(grad_output[0])

            forward_handle = target_layer.register_forward_hook(forward_hook)
            backward_handle = target_layer.register_backward_hook(backward_hook)
            model.eval()
            output = model(image_tensor.unsqueeze(0).to(self.device))
            pred_idx = output.argmax(dim=1).item()
            model.zero_grad()
            output[0, pred_idx].backward()
            grad = gradients[0]
            act = activations[0]
            forward_handle.remove()
            backward_handle.remove()
            weights = grad.mean(dim=(2, 3), keepdim=True)
            cam = (weights * act).sum(dim=1, keepdim=True)
            cam = torch.relu(cam)
            cam = cam.squeeze().cpu().numpy()
            cam = cv2.resize(cam, (self.image_size, self.image_size))
            cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
            return cam, pred_idx
        except Exception as e:
            print(f"Error creating Grad-CAM: {e}")
            return None, None

    def visualize_grad_cam(
        self, disease_type, test_loader, num_samples=3, target_layer="features.8"
    ):
        """Visualize Grad-CAM for sample images"""
        model = self.models[disease_type]
        data_iter = iter(test_loader)
        try:
            images, labels = next(data_iter)
        except StopIteration:
            print("No data available for Grad-CAM visualization")
            return
        fig, axes = plt.subplots(num_samples, 3, figsize=(15, 5 * num_samples))
        if num_samples == 1:
            axes = axes.reshape(1, -1)
        for i in range(min(num_samples, len(images))):
            img_tensor = images[i]
            original_img = img_tensor.permute(1, 2, 0).numpy()
            mean = np.array([0.485, 0.456, 0.406])
            std = np.array([0.229, 0.224, 0.225])
            original_img = original_img * std + mean
            original_img = np.clip(original_img, 0, 1)
            cam, pred_idx = self.create_grad_cam(model, img_tensor, target_layer)
            if cam is not None:
                cam_resized = cv2.resize(cam, (self.image_size, self.image_size))
                heatmap = cv2.applyColorMap(
                    np.uint8(255 * cam_resized), cv2.COLORMAP_JET
                )
                heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
                superimposed = cv2.addWeighted(
                    np.uint8(original_img * 255), 0.6, heatmap, 0.4, 0
                )
                axes[i, 0].imshow(original_img)
                axes[i, 0].set_title("Original Image")
                axes[i, 0].axis("off")
                axes[i, 1].imshow(cam_resized, cmap="jet")
                axes[i, 1].set_title("Grad-CAM Heatmap")
                axes[i, 1].axis("off")
                axes[i, 2].imshow(superimposed)
                true_class = self.class_names[disease_type][labels[i].item()]
                pred_class = self.class_names[disease_type][pred_idx]
                axes[i, 2].set_title(
                    f"Superimposed\nTrue: {true_class}\nPred: {pred_class}"
                )
                axes[i, 2].axis("off")
            else:
                axes[i, 0].imshow(original_img)
                axes[i, 0].set_title("Original Image")
                axes[i, 0].axis("off")
                for j in range(1, 3):
                    axes[i, j].text(
                        0.5,
                        0.5,
                        "Grad-CAM failed",
                        ha="center",
                        va="center",
                        transform=axes[i, j].transAxes,
                    )
                    axes[i, j].axis("off")
        plt.show()


def main():
    """Main function to run the complete pipeline"""
    print("\n" + "=" * 60)
    print("MEDICAL IMAGE CLASSIFICATION SYSTEM")
    print("=" * 60)
    classifier = GPUMedicalClassifier(image_size=224, batch_size=32)
    diseases = ["brain_tumor", "pnemonia"]
    for disease in diseases:
        try:
            model, test_loader = classifier.train_model(disease, epochs=20)
            print(
                f"\nGenerating Grad-CAM visualizations for {disease.replace('_', ' ').title()}..."
            )
            classifier.visualize_grad_cam(disease, test_loader, num_samples=3)
            print(
                f"\n{disease.replace('_', ' ').title()} detection model trained successfully!"
            )
        except Exception as e:
            print(f"Error training {disease} model: {e}")
            continue
    print(f"\nTRAINING COMPLETE!")
    print("=" * 60)
    print("Models saved as:")
    print("   best_brain_tumor_model.pth")
    print("   best_pnemonia_model.pth")
    print("=" * 60)
    print("Ready for predictions! Run: python predict.py")


if __name__ == "__main__":
    main()
