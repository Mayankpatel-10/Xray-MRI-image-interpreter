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


class BrainTumorClassifier:
    """Brain tumor image classifier"""

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
        
        self.train_transform = transforms.Compose([
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
        ])
        self.test_transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            ),
        ])
        self.class_names = []

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

    def create_data_loaders(self, data_path):
        """Create data loaders for brain tumor training and testing"""
        train_dir = os.path.join(data_path, "brain_tumor", "Training")
        test_dir = os.path.join(data_path, "brain_tumor", "Testing")
        
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
        
        self.class_names = train_dataset.dataset.classes
        return train_loader, val_loader, test_loader

    def train_model(self, epochs=20):
        """Train the brain tumor model"""
        print("\n" + "="*60)
        print("BRAIN TUMOR DETECTION TRAINING")
        print("="*60)
        
        train_loader, val_loader, test_loader = self.create_data_loaders("../data")
        num_classes = len(self.class_names)
        print(f"Number of classes: {num_classes}")
        print(f"Class names: {self.class_names}")
        
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
                torch.save(model.state_dict(), "best_brain_tumor_model.pth")
        
        self.plot_training_history(train_losses, val_losses, train_accs, val_accs)
        self.evaluate_model(model, test_loader)
        return model, test_loader

    def plot_training_history(self, train_losses, val_losses, train_accs, val_accs):
        """Plot training history"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        ax1.plot(train_losses, label="Training Loss")
        ax1.plot(val_losses, label="Validation Loss")
        ax1.set_title("Brain Tumor - Model Loss")
        ax1.set_xlabel("Epoch")
        ax1.set_ylabel("Loss")
        ax1.legend()
        ax1.grid(True)
        ax2.plot(train_accs, label="Training Accuracy")
        ax2.plot(val_accs, label="Validation Accuracy")
        ax2.set_title("Brain Tumor - Model Accuracy")
        ax2.set_xlabel("Epoch")
        ax2.set_ylabel("Accuracy (%)")
        ax2.legend()
        ax2.grid(True)
        plt.show()

    def evaluate_model(self, model, test_loader):
        """Evaluate model on test set"""
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
        
        print("\nBrain Tumor - Test Results:")
        print(classification_report(
            all_targets,
            all_predictions,
            target_names=self.class_names,
        ))
        
        cm = confusion_matrix(all_targets, all_predictions)
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=self.class_names,
            yticklabels=self.class_names,
        )
        plt.title("Brain Tumor - Confusion Matrix")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.show()


def main():
    """Main function to run brain tumor training"""
    classifier = BrainTumorClassifier(image_size=224, batch_size=32)
    model, test_loader = classifier.train_model(epochs=20)
    print("\nBrain tumor detection model trained successfully!")
    print("Model saved as: best_brain_tumor_model.pth")


if __name__ == "__main__":
    main()
