import os
import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms, models
import torch.nn.functional as F
import warnings

warnings.filterwarnings("ignore")
try:
    import google.colab

    IS_COLAB = True
except ImportError:
    IS_COLAB = False
if IS_COLAB:
    from google.colab import files
else:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        print("Warning: Tkinter not found. File browser will not be available locally.")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class EasyMedicalPredictor:
    """Main class for medical image prediction"""

    def __init__(self, image_size=224):
        self.image_size = image_size
        self.device = device
        self.is_colab = IS_COLAB
        self.transform = transforms.Compose(
            [
                transforms.Resize((image_size, image_size)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )
        self.brain_tumor_classes = ["glioma", "meningioma", "notumor", "pituitary"]
        self.pneumonia_classes = ["NORMAL", "PNEUMONIA"]
        self.brain_tumor_model = None
        self.pneumonia_model = None
        print("Easy Medical Image Predictor")
        print("=" * 40)
        print(f"Environment: {'Google Colab' if self.is_colab else 'Local Machine'}")
        print("=" * 40)

    def load_models(self):
        """Load trained models from the local directory"""
        models_loaded = 0
        if os.path.exists("best_brain_tumor_model.pth"):
            try:
                self.brain_tumor_model = models.efficientnet_b0(pretrained=False)
                num_ftrs = self.brain_tumor_model.classifier[1].in_features
                self.brain_tumor_model.classifier[1] = nn.Linear(num_ftrs, 4)
                self.brain_tumor_model.load_state_dict(
                    torch.load("best_brain_tumor_model.pth", map_location=self.device)
                )
                self.brain_tumor_model = self.brain_tumor_model.to(self.device).eval()
                print("[SUCCESS] Brain tumor model loaded")
                models_loaded += 1
            except Exception as e:
                print(f"[ERROR] Error loading brain tumor model: {e}")
        if os.path.exists("best_pneumonia_model.pth"):
            try:
                self.pneumonia_model = models.efficientnet_b0(pretrained=False)
                num_ftrs = self.pneumonia_model.classifier[1].in_features
                self.pneumonia_model.classifier[1] = nn.Linear(num_ftrs, 2)
                self.pneumonia_model.load_state_dict(
                    torch.load("best_pneumonia_model.pth", map_location=self.device)
                )
                self.pneumonia_model = self.pneumonia_model.to(self.device).eval()
                print("[SUCCESS] Pneumonia model loaded")
                models_loaded += 1
            except Exception as e:
                print(f"[ERROR] Error loading pneumonia model: {e}")
        return models_loaded

    def select_image_file(self):
        """Select image file based on environment"""
        if self.is_colab:
            print("\nSelect image to upload:")
            uploaded = files.upload()
            return list(uploaded.keys()) if uploaded else None
        else:
            try:
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                file_path = filedialog.askopenfilename(
                    title="Select medical image",
                    filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")],
                )
                root.destroy()
                return [file_path] if file_path else None
            except:
                path = input("Enter path to image: ").strip()
                return [path] if path else None

    def preprocess_image(self, image_path):
        try:
            image = Image.open(image_path).convert("RGB")
            original_image = image.copy()
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            return image_tensor, original_image
        except Exception as e:
            print(f"Error loading {image_path}: {e}")
            return None, None

    def predict_brain_tumor(self, image_tensor):
        if not self.brain_tumor_model:
            return None, None, None
        with torch.no_grad():
            outputs = self.brain_tumor_model(image_tensor)
            probabilities = F.softmax(outputs, dim=1).cpu().numpy().flatten()
            confidence, predicted = torch.max(F.softmax(outputs, dim=1), 1)
            return (
                self.brain_tumor_classes[predicted.item()],
                confidence.item(),
                probabilities,
            )

    def predict_pneumonia(self, image_tensor):
        if not self.pneumonia_model:
            return None, None, None
        with torch.no_grad():
            outputs = self.pneumonia_model(image_tensor)
            probabilities = F.softmax(outputs, dim=1).cpu().numpy().flatten()
            confidence, predicted = torch.max(F.softmax(outputs, dim=1), 1)
            return (
                self.pneumonia_classes[predicted.item()],
                confidence.item(),
                probabilities,
            )

    def create_grad_cam(self, model, image_tensor):
        """Standard PyTorch Grad-CAM implementation (Fixes the mixed TF/Torch bug)"""
        try:
            gradients = []
            activations = []

            def save_grad(m, gi, go):
                gradients.append(go[0])

            def save_act(m, i, o):
                activations.append(o)

            target_layer = None
            for module in model.modules():
                if isinstance(module, nn.Conv2d):
                    target_layer = module
            if not target_layer:
                return None
            h1 = target_layer.register_forward_hook(save_act)
            h2 = target_layer.register_full_backward_hook(save_grad)
            model.zero_grad()
            output = model(image_tensor)
            pred_idx = output.argmax().item()
            output[0, pred_idx].backward()
            h1.remove()
            h2.remove()
            weights = torch.mean(gradients[0], dim=(2, 3), keepdim=True)
            cam = (
                torch.relu(torch.sum(weights * activations[0], dim=1))
                .squeeze()
                .detach()
                .cpu()
                .numpy()
            )
            if cam.max() > cam.min():
                cam = (cam - cam.min()) / (cam.max() - cam.min())
            return cam
        except Exception as e:
            print(f"Visualization error: {e}")
            return None

    def classify_disease_type(self, image_tensor):
        """Classify whether the image is brain tumor or pneumonia"""
        b_class, b_conf, b_probs = self.predict_brain_tumor(image_tensor)
        p_class, p_conf, p_probs = self.predict_pneumonia(image_tensor)
        results = []
        if b_class:
            results.append({"disease": "Brain Tumor", "confidence": b_conf})
        if p_class:
            results.append({"disease": "Pneumonia", "confidence": p_conf})
        if not results:
            return None, None
        best = max(results, key=lambda x: x["confidence"])
        return best["disease"], best["confidence"]

    def predict_and_visualize(self, image_path, disease_type):
        """Main analysis function - preserved functionality and visuals"""
        print(f"\nAnalyzing: {os.path.basename(image_path)}")
        image_tensor, original_image = self.preprocess_image(image_path)
        if image_tensor is None:
            return
        actual_disease, disease_confidence = self.classify_disease_type(image_tensor)
        if actual_disease is None:
            print("No models available for prediction")
            return
        print(
            f"\nImage Classification: {actual_disease} (Confidence: {disease_confidence:.1%})"
        )
        print(f"User Selection: {disease_type.replace('_', ' ').title()}")
        if actual_disease.lower().replace(" ", "_") != disease_type:
            print(
                f"\n[WARNING] Image appears to be {actual_disease}, but you selected {disease_type.replace('_', ' ').title()}"
            )
            print(
                "The system will analyze with the appropriate model for the actual disease type."
            )
        if actual_disease == "Brain Tumor":
            b_class, b_conf, b_probs = self.predict_brain_tumor(image_tensor)
            if b_class:
                best = {
                    "disease": "Brain Tumor",
                    "prediction": b_class,
                    "confidence": b_conf,
                    "model": self.brain_tumor_model,
                    "details": b_probs,
                    "classes": self.brain_tumor_classes,
                }
            else:
                print("Brain tumor model not available")
                return
        elif actual_disease == "Pneumonia":
            p_class, p_conf, p_probs = self.predict_pneumonia(image_tensor)
            if p_class:
                best = {
                    "disease": "Pneumonia",
                    "prediction": p_class,
                    "confidence": p_conf,
                    "model": self.pneumonia_model,
                    "details": p_probs,
                    "classes": self.pneumonia_classes,
                }
            else:
                print("Pneumonia model not available")
                return
        else:
            print("Unable to classify disease type")
            return
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Medical Image Analysis Report", fontsize=18, fontweight="bold")
        axes[0, 0].imshow(original_image)
        axes[0, 0].set_title("Original Image", fontweight="bold")
        axes[0, 0].axis("off")
        summary = f"Detection Result\n\n{best['disease']}\n\n{best['prediction'].upper()}\n\nConfidence: {best['confidence']:.1%}"
        bg_col = (
            "lightgreen"
            if best["confidence"] > 0.8
            else "lightyellow"
            if best["confidence"] > 0.6
            else "lightcoral"
        )
        axes[0, 1].text(
            0.5,
            0.5,
            summary,
            ha="center",
            va="center",
            fontsize=14,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=bg_col),
        )
        axes[0, 1].set_title("Primary Detection", fontweight="bold")
        axes[0, 1].axis("off")
        cam = self.create_grad_cam(best["model"], image_tensor)
        if cam is not None:
            cam_map = cv2.applyColorMap(
                np.uint8(255 * cv2.resize(cam, (224, 224))), cv2.COLORMAP_JET
            )
            cam_map = cv2.cvtColor(cam_map, cv2.COLOR_BGR2RGB)
            overlay = cv2.addWeighted(
                np.array(original_image.resize((224, 224))), 0.6, cam_map, 0.4, 0
            )
            axes[1, 0].imshow(overlay)
            axes[1, 0].set_title("Attention Map (Grad-CAM)", fontweight="bold")
        else:
            axes[1, 0].text(
                0.5, 0.5, "Grad-CAM Generation Failed", ha="center", va="center"
            )
        axes[1, 0].axis("off")
        detail_txt = f"Detailed Predictions ({best['disease']}):\n\n"
        for label, prob in zip(best["classes"], best["details"]):
            detail_txt += f"• {label}: {prob:.1%}\n"
        axes[1, 1].text(
            0.1,
            0.5,
            detail_txt,
            ha="left",
            va="center",
            fontsize=11,
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"),
        )
        axes[1, 1].set_title("Detailed Analysis", fontweight="bold")
        axes[1, 1].axis("off")
        plt.show()


def main():
    predictor = EasyMedicalPredictor()
    if predictor.load_models() == 0:
        print("\nFATAL: No trained models found in the current directory.")
        return
    while True:
        print("\n" + "=" * 50)
        print("1. Brain Tumor Prediction")
        print("2. Pneumonia Prediction")
        print("3. Exit")
        choice = input("Select option (1-3): ").strip()
        if choice == "3":
            break
        if choice in ["1", "2"]:
            disease_type = "brain_tumor" if choice == "1" else "pneumonia"
            disease_name = "Brain Tumor" if choice == "1" else "Pneumonia"
            print(f"\nSelected: {disease_name} Prediction")
            file_paths = predictor.select_image_file()
            if file_paths:
                for path in file_paths:
                    try:
                        predictor.predict_and_visualize(path, disease_type)
                    except Exception as e:
                        print(f"Error analyzing {path}: {e}")
        else:
            print("Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
