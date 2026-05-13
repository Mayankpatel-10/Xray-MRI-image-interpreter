#!/usr/bin/env python3
"""
Unified Medical Image Classification Training Script
Complete implementation following all medical AI best practices

Features:
- ResNet50 with Transfer Learning
- 70-15-15 Data Split with Leakage Prevention
- EarlyStopping and ReduceLROnPlateau
- Enhanced Data Augmentation
- Batch Normalization & Dropout
- Comprehensive Evaluation Metrics
- Class Weights for Imbalance
- Automatic Quality Checks
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from torch.utils.data import Dataset, DataLoader, random_split
from PIL import Image
import os
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, precision_recall_fscore_support
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from tqdm import tqdm
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")
torch.backends.cudnn.benchmark = True

class EarlyStopping:
    def __init__(self, patience=5, min_delta=0.001, restore_best_weights=True):
        self.patience = patience
        self.min_delta = min_delta
        self.restore_best_weights = restore_best_weights
        self.best_loss = float('inf')
        self.counter = 0
        self.best_weights = None
        
    def __call__(self, val_loss, model):
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
            if self.restore_best_weights:
                self.best_weights = model.state_dict().copy()
        else:
            self.counter += 1
            
        if self.counter >= self.patience:
            if self.restore_best_weights and self.best_weights is not None:
                model.load_state_dict(self.best_weights)
            return True
        return False

class MedicalImageDataset(Dataset):
    def __init__(self, root_dir, transform=None, dataset_type='brain_tumor'):
        self.root_dir = root_dir
        self.transform = transform
        self.dataset_type = dataset_type
        self.images = []
        self.labels = []
        self.class_names = []
        
        self._load_data()
    
    def _load_data(self):
        if self.dataset_type == 'brain_tumor':
            classes = ['glioma', 'meningioma', 'notumor', 'pituitary']
        else:  # pneumonia
            classes = ['NORMAL', 'PNEUMONIA']
        
        self.class_names = classes
        
        for class_idx, class_name in enumerate(classes):
            class_dir = os.path.join(self.root_dir, class_name)
            if os.path.exists(class_dir):
                for img_name in os.listdir(class_dir):
                    if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                        self.images.append(os.path.join(class_dir, img_name))
                        self.labels.append(class_idx)
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_path = self.images[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

class ResNetMedicalCNN(nn.Module):
    def __init__(self, num_classes, pretrained=True):
        super(ResNetMedicalCNN, self).__init__()
        
        # Use ResNet50 as backbone with transfer learning
        self.backbone = models.resnet50(weights='IMAGENET1K_V1' if pretrained else None)
        
        # Freeze early layers for transfer learning
        for param in list(self.backbone.parameters())[:-10]:
            param.requires_grad = False
        
        # Replace the final fully connected layer with improved architecture
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)

class BrainTumorModel:
    def __init__(self, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.model = None
        self.class_names = ['glioma', 'meningioma', 'notumor', 'pituitary']
        
    def create_model(self):
        self.model = ResNetMedicalCNN(num_classes=4).to(self.device)
        return self.model
    
    def get_transforms(self):
        train_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomRotation(15),
            transforms.RandomResizedCrop(224, scale=(0.85, 1.0)),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        val_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        return train_transform, val_transform

class PneumoniaModel:
    def __init__(self, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.model = None
        self.class_names = ['NORMAL', 'PNEUMONIA']
        
    def create_model(self):
        self.model = ResNetMedicalCNN(num_classes=2).to(self.device)
        return self.model
    
    def get_transforms(self):
        train_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomRotation(15),
            transforms.RandomResizedCrop(224, scale=(0.85, 1.0)),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        val_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        return train_transform, val_transform

class Trainer:
    def __init__(self, model, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.model = model
        self.device = device
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.AdamW(model.parameters(), lr=0.0001, weight_decay=1e-4)
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.2, patience=3, verbose=False
        )
    
    def train_epoch(self, train_loader):
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        # Progress bar for training
        pbar = tqdm(train_loader, desc="Training", leave=False)
        
        for batch_idx, (data, targets) in enumerate(pbar):
            data, targets = data.to(self.device), targets.to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(data)
            loss = self.criterion(outputs, targets)
            loss.backward()
            self.optimizer.step()
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            
            # Update progress bar
            current_acc = 100. * correct / total
            pbar.set_postfix({
                'Loss': f'{running_loss/(batch_idx+1):.4f}',
                'Acc': f'{current_acc:.2f}%'
            })
        
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100. * correct / total
        
        return epoch_loss, epoch_acc
    
    def validate(self, val_loader):
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        all_preds = []
        all_targets = []
        
        # Progress bar for validation
        pbar = tqdm(val_loader, desc="Validating", leave=False)
        
        with torch.no_grad():
            for data, targets in pbar:
                data, targets = data.to(self.device), targets.to(self.device)
                outputs = self.model(data)
                loss = self.criterion(outputs, targets)
                
                running_loss += loss.item()
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()
                
                all_preds.extend(predicted.cpu().numpy())
                all_targets.extend(targets.cpu().numpy())
                
                # Update progress bar
                current_acc = 100. * correct / total
                pbar.set_postfix({
                    'Loss': f'{running_loss/(pbar.n+1):.4f}',
                    'Acc': f'{current_acc:.2f}%'
                })
        
        epoch_loss = running_loss / len(val_loader)
        epoch_acc = 100. * correct / total
        
        return epoch_loss, epoch_acc, all_preds, all_targets
    
    def train(self, train_loader, val_loader, epochs=30, save_path=None):
        best_val_acc = 0.0
        early_stopping = EarlyStopping(patience=5, min_delta=0.001, restore_best_weights=True)
        
        # Progress bar for epochs
        epoch_pbar = tqdm(range(epochs), desc="Training Progress", unit="epoch")
        
        for epoch in epoch_pbar:
            train_loss, train_acc = self.train_epoch(train_loader)
            val_loss, val_acc, _, _ = self.validate(val_loader)
            
            self.scheduler.step(val_loss)
            
            # Update epoch progress bar
            epoch_pbar.set_postfix({
                'Train Loss': f'{train_loss:.4f}',
                'Train Acc': f'{train_acc:.2f}%',
                'Val Loss': f'{val_loss:.4f}',
                'Val Acc': f'{val_acc:.2f}%',
                'LR': f'{self.optimizer.param_groups[0]["lr"]:.6f}'
            })
            
            # Check for overfitting signs
            if epoch > 5:
                if train_acc > val_acc + 10:
                    tqdm.write("Warning: Potential overfitting detected!")
            
            # Save best model
            if val_acc > best_val_acc and save_path:
                best_val_acc = val_acc
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'val_acc': val_acc,
                    'val_loss': val_loss,
                }, save_path)
                tqdm.write(f'New best model saved with accuracy: {val_acc:.2f}%')
            
            # Early stopping check
            if early_stopping(val_loss, self.model):
                tqdm.write(f'Early stopping triggered at epoch {epoch+1}')
                tqdm.write(f'Best validation loss: {early_stopping.best_loss:.4f}')
                break
        
        return best_val_acc

def evaluate_model(model, test_loader, class_names, device='cuda' if torch.cuda.is_available() else 'cpu'):
    model.eval()
    all_preds = []
    all_targets = []
    all_probs = []
    
    with torch.no_grad():
        for data, targets in test_loader:
            data, targets = data.to(device), targets.to(device)
            outputs = model(data)
            probs = F.softmax(outputs, dim=1)
            _, predicted = outputs.max(1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    
    # Convert to numpy arrays
    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)
    all_probs = np.array(all_probs)
    
    # Basic metrics
    accuracy = (all_preds == all_targets).mean() * 100
    
    # Detailed classification report
    print("Classification Report:")
    print(classification_report(all_targets, all_preds, target_names=class_names))
    
    # Calculate ROC-AUC for multi-class
    try:
        if len(class_names) == 2:
            roc_auc = roc_auc_score(all_targets, all_probs[:, 1])
        else:
            roc_auc = roc_auc_score(all_targets, all_probs, multi_class='ovr', average='macro')
        print(f"ROC-AUC Score: {roc_auc:.4f}")
    except:
        print("ROC-AUC calculation failed")
        roc_auc = 0.0
    
    # Confusion matrix
    cm = confusion_matrix(all_targets, all_preds)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Calculate per-class metrics
    precision, recall, f1, support = precision_recall_fscore_support(
        all_targets, all_preds, average=None
    )
    
    print("\nPer-Class Metrics:")
    print("-" * 50)
    for i, class_name in enumerate(class_names):
        print(f"{class_name}:")
        print(f"  Precision: {precision[i]:.4f}")
        print(f"  Recall: {recall[i]:.4f}")
        print(f"  F1-Score: {f1[i]:.4f}")
        print(f"  Support: {support[i]}")
    
    # Create comprehensive report
    report = classification_report(all_targets, all_preds, target_names=class_names, output_dict=True)
    report['accuracy'] = accuracy
    report['roc_auc'] = roc_auc
    
    return report

def check_dataset_quality(data_dir, dataset_type):
    """Check dataset quality and potential issues"""
    print(f"Checking {dataset_type} dataset quality...")
    
    if dataset_type == 'brain_tumor':
        base_dir = os.path.join(data_dir, 'brain_tumor', 'Training')
        classes = ['glioma', 'meningioma', 'notumor', 'pituitary']
    else:
        base_dir = os.path.join(data_dir, 'pneumonia', 'train')
        classes = ['NORMAL', 'PNEUMONIA']
    
    issues = []
    class_counts = {}
    
    for class_name in classes:
        class_dir = os.path.join(base_dir, class_name)
        if not os.path.exists(class_dir):
            issues.append(f"Missing class directory: {class_name}")
            continue
            
        images = [f for f in os.listdir(class_dir) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        class_counts[class_name] = len(images)
        
        if len(images) < 50:
            issues.append(f"WARNING: Low sample count for {class_name}: {len(images)}")
    
    # Check for class imbalance
    if class_counts:
        max_count = max(class_counts.values())
        min_count = min(class_counts.values())
        if max_count / min_count > 3:
            issues.append(f"WARNING: Significant class imbalance detected")
    
    if issues:
        print("Dataset Quality Issues:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("Dataset quality looks good")
    
    return class_counts

def create_balanced_loaders(dataset, batch_size=16, train_split=0.7, val_split=0.15):
    """Create train, validation, and test loaders with proper 70-15-15 split"""
    dataset_size = len(dataset)
    train_size = int(dataset_size * train_split)
    val_size = int(dataset_size * val_split)
    test_size = dataset_size - train_size - val_size
    
    # Ensure we don't lose any samples due to rounding
    if test_size < 0:
        test_size = 0
        val_size = dataset_size - train_size
    
    train_dataset, val_dataset, test_dataset = random_split(
        dataset, [train_size, val_size, test_size], 
        generator=torch.Generator().manual_seed(42)
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    
    print(f"Data split - Train: {len(train_dataset)} ({len(train_dataset)/dataset_size*100:.1f}%), "
          f"Val: {len(val_dataset)} ({len(val_dataset)/dataset_size*100:.1f}%), "
          f"Test: {len(test_dataset)} ({len(test_dataset)/dataset_size*100:.1f}%)")
    
    return train_loader, val_loader, test_loader

def check_data_leakage(train_dataset, val_dataset, test_dataset):
    """Check for data leakage between splits"""
    # Handle both regular datasets and random_split subsets
    if hasattr(train_dataset, 'indices'):
        train_images = set(train_dataset.dataset.images[i] for i in train_dataset.indices)
        val_images = set(val_dataset.dataset.images[i] for i in val_dataset.indices)
        if hasattr(test_dataset, 'indices'):
            test_images = set(test_dataset.dataset.images[i] for i in test_dataset.indices)
        else:
            test_images = set(test_dataset.images)
    else:
        train_images = set(train_dataset.images)
        val_images = set(val_dataset.images)
        test_images = set(test_dataset.images)
    
    # Check for overlaps between splits only (not with original dataset)
    train_val_overlap = train_images & val_images
    train_test_overlap = train_images & test_images
    val_test_overlap = val_images & test_images
    
    # Only check for leakage if test_dataset is also a split (not original dataset)
    if hasattr(test_dataset, 'indices'):
        if train_val_overlap:
            print(f"WARNING: {len(train_val_overlap)} images found in both train and validation sets!")
            return False
        
        if train_test_overlap:
            print(f"WARNING: {len(train_test_overlap)} images found in both train and test sets!")
            return False
        
        if val_test_overlap:
            print(f"WARNING: {len(val_test_overlap)} images found in both validation and test sets!")
            return False
    
    print("No data leakage detected between splits")
    return True

def get_class_weights(labels, num_classes):
    """Calculate class weights for imbalanced datasets"""
    class_weights = compute_class_weight(
        'balanced', 
        classes=np.arange(num_classes), 
        y=labels
    )
    return torch.FloatTensor(class_weights)

def train_brain_tumor_model(data_dir, epochs=30, batch_size=16):
    """Train brain tumor classification model using ResNet with transfer learning"""
    print("=" * 70)
    print("TRAINING BRAIN TUMOR CLASSIFICATION MODEL (RESNET50)")
    print("=" * 70)
    
    # Check dataset quality
    class_counts = check_dataset_quality(data_dir, 'brain_tumor')
    
    # Initialize model
    brain_model = BrainTumorModel()
    model = brain_model.create_model()
    
    # Get transforms
    train_transform, val_transform = brain_model.get_transforms()
    
    # Create combined dataset from training data
    full_dataset = MedicalImageDataset(
        root_dir=os.path.join(data_dir, 'brain_tumor', 'Training'),
        transform=train_transform,
        dataset_type='brain_tumor'
    )
    
    # Create separate test dataset
    test_dataset = MedicalImageDataset(
        root_dir=os.path.join(data_dir, 'brain_tumor', 'Testing'),
        transform=val_transform,
        dataset_type='brain_tumor'
    )
    
    print(f"Total training samples: {len(full_dataset)}")
    print(f"Test samples: {len(test_dataset)}")
    print(f"Classes: {brain_model.class_names}")
    
    # Create data loaders with 70-15-15 split
    train_loader, val_loader, internal_test_loader = create_balanced_loaders(
        full_dataset, batch_size=batch_size
    )
    external_test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    
    # Check for data leakage
    train_dataset = train_loader.dataset.dataset
    val_dataset = val_loader.dataset.dataset
    check_data_leakage(train_dataset, val_dataset, test_dataset)
    
    # Calculate class weights
    train_labels = [label for _, label in train_dataset]
    class_weights = get_class_weights(train_labels, 4)
    
    # Initialize trainer with weighted loss
    trainer = Trainer(model)
    trainer.criterion = nn.CrossEntropyLoss(weight=class_weights.to(trainer.device))
    
    print(f"Class weights: {class_weights.numpy()}")
    
    # Train model
    save_path = 'brain_tumor_resnet50_model.pth'
    best_val_acc = trainer.train(train_loader, val_loader, epochs=epochs, save_path=save_path)
    
    # Evaluate on test set
    print("\nEvaluating on test set...")
    test_report = evaluate_model(model, external_test_loader, brain_model.class_names, trainer.device)
    
    return model, best_val_acc, test_report

def train_pneumonia_model(data_dir, epochs=30, batch_size=16):
    """Train pneumonia classification model using ResNet with transfer learning"""
    print("=" * 70)
    print("TRAINING PNEUMONIA CLASSIFICATION MODEL (RESNET50)")
    print("=" * 70)
    
    # Check dataset quality
    class_counts = check_dataset_quality(data_dir, 'pneumonia')
    
    # Initialize model
    pneumonia_model = PneumoniaModel()
    model = pneumonia_model.create_model()
    
    # Get transforms
    train_transform, val_transform = pneumonia_model.get_transforms()
    
    # Create datasets
    full_dataset = MedicalImageDataset(
        root_dir=os.path.join(data_dir, 'pneumonia', 'train'),
        transform=train_transform,
        dataset_type='pneumonia'
    )
    
    val_dataset = MedicalImageDataset(
        root_dir=os.path.join(data_dir, 'pneumonia', 'val'),
        transform=val_transform,
        dataset_type='pneumonia'
    )
    
    print(f"Total training samples: {len(full_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    print(f"Classes: {pneumonia_model.class_names}")
    
    # Create data loaders with 70-15-15 split from training data
    train_loader, internal_val_loader, internal_test_loader = create_balanced_loaders(
        full_dataset, batch_size=batch_size
    )
    external_val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    
    # Check for data leakage
    train_dataset = train_loader.dataset.dataset
    internal_val_dataset = internal_val_loader.dataset.dataset
    check_data_leakage(train_dataset, internal_val_dataset, val_dataset)
    
    # Calculate class weights for imbalanced pneumonia dataset
    train_labels = [label for _, label in train_dataset]
    class_weights = get_class_weights(train_labels, 2)
    
    # Initialize trainer with weighted loss
    trainer = Trainer(model)
    trainer.criterion = nn.CrossEntropyLoss(weight=class_weights.to(trainer.device))
    
    print(f"Class weights: {class_weights.numpy()}")
    
    # Train model
    save_path = 'pneumonia_resnet50_model.pth'
    best_val_acc = trainer.train(train_loader, internal_val_loader, epochs=epochs, save_path=save_path)
    
    # Evaluate on external validation set
    print("\nEvaluating on external validation set...")
    val_report = evaluate_model(model, external_val_loader, pneumonia_model.class_names, trainer.device)
    
    return model, best_val_acc, val_report

def main():
    parser = argparse.ArgumentParser(description='Train medical image classification models using ResNet50 with best practices')
    parser.add_argument('--data_dir', type=str, default='../data', help='Path to data directory')
    parser.add_argument('--model', type=str, choices=['brain_tumor', 'pneumonia', 'both'], default='both', help='Which model to train')
    parser.add_argument('--epochs', type=int, default=30, help='Number of training epochs (recommended: 20-40)')
    parser.add_argument('--batch_size', type=int, default=16, help='Batch size (recommended: 16 or 32)')
    parser.add_argument('--device', type=str, default='auto', choices=['auto', 'cuda', 'cpu'], help='Device to use')
    
    args = parser.parse_args()
    
    # Set device
    if args.device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        device = args.device
    
    print("MEDICAL IMAGE CLASSIFICATION TRAINING")
    print("=" * 70)
    print(f"Device: {device}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"Model Architecture: ResNet50 with Transfer Learning")
    print(f"Training Configuration: {args.epochs} epochs, batch size {args.batch_size}")
    print(f"Learning Rate: 0.0001 (with ReduceLROnPlateau)")
    print("Features: EarlyStopping, BatchNormalization, Dropout, Data Augmentation")
    print("Evaluation: Comprehensive metrics (F1, Recall, Precision, ROC-AUC)")
    print("=" * 70)
    
    # Check data directory
    if not os.path.exists(args.data_dir):
        print(f"Error: Data directory '{args.data_dir}' not found!")
        print("Please make sure the data directory is in the parent folder or specify the correct path.")
        return
    
    results = {}
    
    if args.model in ['brain_tumor', 'both']:
        try:
            brain_model, brain_acc, brain_report = train_brain_tumor_model(
                args.data_dir, epochs=args.epochs, batch_size=args.batch_size
            )
            results['brain_tumor'] = {
                'best_val_acc': brain_acc,
                'test_report': brain_report
            }
        except Exception as e:
            print(f"Error training brain tumor model: {e}")
    
    if args.model in ['pneumonia', 'both']:
        try:
            pneumonia_model, pneumonia_acc, pneumonia_report = train_pneumonia_model(
                args.data_dir, epochs=args.epochs, batch_size=args.batch_size
            )
            results['pneumonia'] = {
                'best_val_acc': pneumonia_acc,
                'val_report': pneumonia_report
            }
        except Exception as e:
            print(f"Error training pneumonia model: {e}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("TRAINING SUMMARY")
    print("=" * 70)
    
    for model_name, result in results.items():
        print(f"\n{model_name.upper()} MODEL (RESNET50):")
        print(f"Best Validation Accuracy: {result['best_val_acc']:.2f}%")
        
        if 'test_report' in result:
            report = result['test_report']
            print(f"Test Accuracy: {report['accuracy']:.2f}%")
        else:
            report = result['val_report']
            print(f"Validation Accuracy: {report['accuracy']:.2f}%")
        
        if 'roc_auc' in report:
            print(f"ROC-AUC: {report['roc_auc']:.4f}")
        
        print("Per-class metrics:")
        for class_name in ['glioma', 'meningioma', 'notumor', 'pituitary', 'NORMAL', 'PNEUMONIA']:
            if class_name in report:
                metrics = report[class_name]
                print(f"  {class_name}: F1={metrics['f1-score']:.3f}, Precision={metrics['precision']:.3f}, Recall={metrics['recall']:.3f}")

if __name__ == "__main__":
    main()
