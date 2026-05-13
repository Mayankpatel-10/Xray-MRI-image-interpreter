#!/usr/bin/env python3
"""
Compare backend and predict.py image processing pipelines
"""

import os
import sys
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np

# Add ML directory to path
ml_path = os.path.join(os.path.dirname(__file__), '..', 'ml')
sys.path.insert(0, ml_path)

from ml_models import ResNetMedicalCNN, BrainTumorModel, PneumoniaModel

def compare_pipelines():
    """Compare image processing between backend and predict.py"""
    print("=" * 80)
    print("COMPARING IMAGE PROCESSING PIPELINES")
    print("=" * 80)
    
    # Load models
    brain_model_path = '../ml/brain_tumor_resnet50_model.pth'
    
    if os.path.exists(brain_model_path):
        # Backend approach
        print("\n🔧 BACKEND APPROACH:")
        brain_tumor_model = BrainTumorModel()
        model = brain_tumor_model.create_model()
        brain_transform, val_transform = brain_tumor_model.get_transforms()
        
        print(f"Train transform: {brain_transform}")
        print(f"Val transform: {val_transform}")
        
        # Load checkpoint
        checkpoint = torch.load(brain_model_path, map_location='cpu')
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        
        print(f"Model classes: {brain_tumor_model.class_names}")
        print(f"Model device: {next(model.parameters()).device}")
        
        # Test transforms
        print("\n📊 TRANSFORM COMPARISON:")
        print("Backend transform pipeline:")
        for i, transform in enumerate(val_transform.transforms):
            print(f"  {i}: {transform}")
        
        # Predict.py approach (from original script)
        print("\n🔧 PREDICT.PY APPROACH:")
        print("Uses val_transform from get_transforms() method")
        print("Same model architecture and loading")
        
        # Test with sample image
        print("\n🧪 TESTING WITH SAMPLE IMAGE:")
        try:
            # Create a sample image
            sample_image = Image.new('RGB', (224, 224), color='red')
            print(f"Sample image: {sample_image.size}, mode: {sample_image.mode}")
            
            # Apply transforms
            transformed = val_transform(sample_image)
            print(f"Transformed tensor shape: {transformed.shape}")
            print(f"Tensor dtype: {transformed.dtype}")
            print(f"Tensor min/max: {transformed.min():.4f}/{transformed.max():.4f}")
            
            # Make prediction
            with torch.no_grad():
                output = model(transformed.unsqueeze(0))
                probabilities = F.softmax(output, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
                
                print(f"Raw output: {output}")
                print(f"Probabilities: {probabilities}")
                print(f"Predicted: {predicted.item()} ({brain_tumor_model.class_names[predicted.item()]})")
                print(f"Confidence: {confidence.item():.4f}")
                
                # Show all probabilities
                for i, class_name in enumerate(brain_tumor_model.class_names):
                    prob = probabilities[0][i].item() * 100
                    print(f"  {class_name}: {prob:.2f}%")
        
        except Exception as e:
            print(f"Error in testing: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print(f"❌ Model not found: {brain_model_path}")

if __name__ == "__main__":
    compare_pipelines()
