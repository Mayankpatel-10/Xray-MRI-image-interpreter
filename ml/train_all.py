#!/usr/bin/env python3
"""
Main training script that calls individual training scripts
for brain tumor and pneumonia detection models.
"""

import subprocess
import sys
import os
from datetime import datetime

def run_training_script(script_name, model_name):
    """Run a training script and handle errors"""
    print(f"\n{'='*60}")
    print(f"STARTING {model_name.upper()} TRAINING")
    print(f"{'='*60}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run the training script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=7200)  # 2 hour timeout
        
        if result.returncode == 0:
            print(f"\n{'='*60}")
            print(f"{model_name.upper()} TRAINING COMPLETED SUCCESSFULLY!")
            print(f"{'='*60}")
            print("Output:")
            print(result.stdout)
        else:
            print(f"\n{'='*60}")
            print(f"ERROR IN {model_name.upper()} TRAINING!")
            print(f"{'='*60}")
            print("Error output:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n{'='*60}")
        print(f"TIMEOUT: {model_name.upper()} training took too long!")
        print(f"{'='*60}")
        return False
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"EXCEPTION IN {model_name.upper()} TRAINING: {e}")
        print(f"{'='*60}")
        return False
    
    return True

def main():
    """Main function to run all training scripts"""
    print("\n" + "="*80)
    print("MEDICAL IMAGE CLASSIFICATION SYSTEM - COMPLETE TRAINING")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("This will train both brain tumor and pneumonia detection models.")
    print("="*80)
    
    # Change to the ml directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Training scripts to run
    training_scripts = [
        ("train_brain_tumor.py", "Brain Tumor"),
        ("train_pneumonia.py", "Pneumonia")
    ]
    
    success_count = 0
    total_scripts = len(training_scripts)
    
    for script_name, model_name in training_scripts:
        if run_training_script(script_name, model_name):
            success_count += 1
            print(f"\n{model_name} training completed successfully!")
        else:
            print(f"\n{model_name} training failed!")
        
        # Add a small delay between training scripts
        if script_name != training_scripts[-1][0]:  # If not the last script
            print("\nWaiting 5 seconds before starting next training...")
            import time
            time.sleep(5)
    
    # Final summary
    print("\n" + "="*80)
    print("TRAINING SUMMARY")
    print("="*80)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Successfully trained: {success_count}/{total_scripts} models")
    
    if success_count == total_scripts:
        print("\nAll models trained successfully! Ready for predictions.")
        print("Available model files:")
        if os.path.exists("best_brain_tumor_model.pth"):
            print("  - best_brain_tumor_model.pth")
        if os.path.exists("best_pneumonia_model.pth"):
            print("  - best_pneumonia_model.pth")
        print("\nYou can now run predictions with: python predict.py")
    else:
        print("\nSome models failed to train. Check the error messages above.")
    
    print("="*80)

if __name__ == "__main__":
    main()
