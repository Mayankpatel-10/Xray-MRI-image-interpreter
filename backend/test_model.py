#!/usr/bin/env python3
"""
Test script to debug brain tumor model prediction
"""

import os
import sys
import torch
from PIL import Image
import numpy as np

# Add ML directory to path
ml_path = os.path.join(os.path.dirname(__file__), '..', 'ml')
sys.path.insert(0, ml_path)

from ml_models import ResNetMedicalCNN, BrainTumorModel, PneumoniaModel

def test_brain_model():
    """Test brain tumor model with debug output"""
    print("=" * 60)
    print("TESTING BRAIN TUMOR MODEL")
    print("=" * 60)
    
    # Check model file
    model_path = '../ml/brain_tumor_resnet50_model.pth'
    print(f"Model path: {model_path}")
    print(f"Model exists: {os.path.exists(model_path)}")
    
    if not os.path.exists(model_path):
        print("❌ Model file not found!")
        return
    
    try:
        # Load model
        print("🔄 Loading brain tumor model...")
        brain_tumor_model = BrainTumorModel()
        model = brain_tumor_model.create_model()
        brain_transform, _ = brain_tumor_model.get_transforms()
        
        # Load checkpoint
        checkpoint = torch.load(model_path, map_location='cpu')
        print(f"Checkpoint keys: {list(checkpoint.keys())}")
        
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        
        print(f"✅ Model loaded successfully")
        print(f"Model classes: {brain_tumor_model.class_names}")
        print(f"Model architecture: {type(model)}")
        
        # Test with a dummy tensor
        dummy_input = torch.randn(1, 3, 224, 224)
        with torch.no_grad():
            output = model(dummy_input)
            print(f"Dummy output shape: {output.shape}")
            print(f"Dummy output: {output}")
            
            probabilities = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            print(f"Predicted class index: {predicted.item()}")
            print(f"Confidence: {confidence.item()}")
            
            # Show all probabilities
            for i, class_name in enumerate(brain_tumor_model.class_names):
                prob = probabilities[0][i].item() * 100
                print(f"{class_name}: {prob:.2f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_brain_model()
