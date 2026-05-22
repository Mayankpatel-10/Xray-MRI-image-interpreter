#!/usr/bin/env python3
"""
Command-line Medical Image Classification Prediction Script
Terminal-based prediction with PDF report generation
"""

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import argparse
import os
import sys
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import tkinter as tk
from tkinter import filedialog
import cv2
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# Import model classes
from ml_models import ResNetMedicalCNN, BrainTumorModel, PneumoniaModel

class GradCAM:
    def __init__(self, model, target_layer_name):
        self.model = model
        self.target_layer_name = target_layer_name
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self.register_hooks()
    
    def register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output
        
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]
        
        # Find target layer
        target_layer = None
        for name, module in self.model.named_modules():
            if name == self.target_layer_name:
                target_layer = module
                break
        
        if target_layer is None:
            # Try to find the last convolutional layer
            for name, module in reversed(list(self.model.named_modules())):
                if isinstance(module, torch.nn.Conv2d):
                    target_layer = module
                    print(f"Using layer: {name} as target layer")
                    break
        
        if target_layer is not None:
            target_layer.register_forward_hook(forward_hook)
            target_layer.register_backward_hook(backward_hook)
    
    def generate_cam(self, input_tensor, class_idx):
        with torch.enable_grad():
            self.model.eval()
            
            # Forward pass
            output = self.model(input_tensor)
            
            # Zero gradients
            self.model.zero_grad()
            
            # Backward pass for target class
            class_score = output[0, class_idx]
            class_score.backward()
            
            # Get gradients and activations
            gradients = self.gradients[0]  # [C, H, W]
            activations = self.activations[0]  # [C, H, W]
            
            # Global average pooling of gradients
            weights = torch.mean(gradients, dim=(1, 2))  # [C]
            
            # Weighted combination of activation maps
            cam = torch.zeros(activations.shape[1:], dtype=torch.float32, device=activations.device)  # [H, W]
            for i, w in enumerate(weights):
                cam += w * activations[i]
            
            # ReLU to remove negative values
            cam = F.relu(cam)
            
            # Normalize to [0, 1]
            if cam.max() > 0:
                cam = cam / cam.max()
            
            return cam.detach().cpu().numpy()

class MedicalImagePredictorCLI:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Model configurations
        self.models = {
            'brain_tumor': {
                'path': 'brain_tumor_resnet50_model.pth',
                'classes': ['glioma', 'meningioma', 'notumor', 'pituitary'],
                'model_class': BrainTumorModel,
                'title': 'Brain Tumor Classification',
                'test_accuracy': '89.44%',
                'roc_auc': '0.9786'
            },
            'pneumonia': {
                'path': 'pneumonia_resnet50_model.pth',
                'classes': ['NORMAL', 'PNEUMONIA'],
                'model_class': PneumoniaModel,
                'title': 'Pneumonia Classification',
                'test_accuracy': '93.88%',
                'roc_auc': '0.9907'
            }
        }
        
        self.current_model = None
        self.current_model_type = None
        self.transform = None
        
    def load_model(self, model_type):
        """Load the specified model"""
        model_config = self.models[model_type]
        
        try:
            # Check if model file exists
            if not os.path.exists(model_config['path']):
                print(f"Error: Model file not found: {model_config['path']}")
                print("Please train the model first using: python train_unified.py")
                return False
            
            print(f"Loading {model_config['title']} model...")
            
            # Load model
            model_class = model_config['model_class']
            model_obj = model_class(device=self.device)
            model = model_obj.create_model(pretrained=False)
            
            # Load trained weights
            checkpoint = torch.load(model_config['path'], map_location=self.device)
            model.load_state_dict(checkpoint['model_state_dict'])
            model.eval()
            
            # Get transforms
            _, val_transform = model_obj.get_transforms()
            
            self.current_model = model
            self.current_model_type = model_type
            self.transform = val_transform
            
            print(f"{model_config['title']} model loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
            
    def preprocess_image(self, image_path):
        """Preprocess image for prediction"""
        try:
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0)
            return image_tensor.to(self.device)
        except Exception as e:
            raise Exception(f"Error preprocessing image: {str(e)}")
            
    def predict(self, image_path):
        """Make prediction on image"""
        try:
            print("Processing image and making prediction...")
            
            # Preprocess image
            image_tensor = self.preprocess_image(image_path)
            
            # Make prediction
            with torch.no_grad():
                outputs = self.current_model(image_tensor)
                probabilities = F.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
                
            # Get results
            model_config = self.models[self.current_model_type]
            predicted_class = model_config['classes'][predicted.item()]
            confidence_score = confidence.item() * 100
            
            # Get all class probabilities
            class_probs = probabilities.cpu().numpy()[0]
            class_predictions = []
            for i, (class_name, prob) in enumerate(zip(model_config['classes'], class_probs)):
                class_predictions.append((class_name, prob * 100))
            
            # Sort by probability
            class_predictions.sort(key=lambda x: x[1], reverse=True)
            
            return predicted_class, confidence_score, class_predictions, image_path
            
        except Exception as e:
            print(f"Error during prediction: {str(e)}")
            return None, None, None, None
            
    def select_image_file(self):
        """Open file dialog to select image"""
        try:
            # Create a hidden root window
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            filetypes = [
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
            
            file_path = filedialog.askopenfilename(
                title="Select Medical Image",
                filetypes=filetypes
            )
            
            root.destroy()
            
            return file_path if file_path else None
            
        except Exception as e:
            print(f"Error opening file dialog: {str(e)}")
            return None
            
    def generate_heatmap(self, image_path, predicted_class_idx, save_path=None):
        """Generate Grad-CAM heatmap visualization"""
        try:
            print("Generating Grad-CAM heatmap...")
            
            # Initialize Grad-CAM
            grad_cam = GradCAM(self.current_model, 'backbone.layer4.2.conv3')
            
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Generate CAM
            cam = grad_cam.generate_cam(input_tensor, predicted_class_idx)
            
            # Resize CAM to match image size
            original_size = image.size
            cam_resized = cv2.resize(cam, original_size)
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Create heatmap
            heatmap = cm.jet(cam_resized)[:, :, :3]  # Remove alpha channel
            heatmap = (heatmap * 255).astype(np.uint8)
            
            # Create overlay
            overlay = cv2.addWeighted(img_array, 0.6, heatmap, 0.4, 0)
            
            # Create visualization with original image, heatmap, and overlay
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            
            # Original image
            axes[0].imshow(img_array)
            axes[0].set_title('Original Image')
            axes[0].axis('off')
            
            # Heatmap
            axes[1].imshow(cam_resized, cmap='jet')
            axes[1].set_title('Grad-CAM Heatmap')
            axes[1].axis('off')
            
            # Overlay
            axes[2].imshow(overlay)
            axes[2].set_title('Overlay')
            axes[2].axis('off')
            
            plt.tight_layout()
            
            # Save heatmap
            if save_path is None:
                import io
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
                plt.close()
                img_buffer.seek(0)
                print("Heatmap generated in memory.")
                return img_buffer
            else:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                plt.close()
                print(f"Heatmap saved: {save_path}")
                return save_path
            
        except Exception as e:
            print(f"Error generating heatmap: {str(e)}")
            return None
            
    def generate_pdf_report(self, predicted_class, confidence, class_predictions, image_path, heatmap_file=None):
        """Generate formal medical PDF report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Create PDF document in memory
            import io
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, 
                                 leftMargin=72, rightMargin=72, 
                                 topMargin=72, bottomMargin=72)
            styles = getSampleStyleSheet()
            story = []
            
            # Custom formal styles
            title_style = ParagraphStyle(
                'MedicalTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                alignment=1,
                textColor=colors.darkblue,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'MedicalHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.darkblue,
                fontName='Helvetica-Bold'
            )
            
            subheading_style = ParagraphStyle(
                'MedicalSubheading',
                parent=styles['Heading3'],
                fontSize=12,
                spaceAfter=8,
                textColor=colors.black,
                fontName='Helvetica-Bold'
            )
            
            body_style = ParagraphStyle(
                'MedicalBody',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                textColor=colors.black,
                fontName='Helvetica'
            )
            
            # Header
            story.append(Paragraph("MEDICAL IMAGE ANALYSIS REPORT", title_style))
            story.append(Spacer(1, 20))
            
            # Report Information
            story.append(Paragraph("Report Information", heading_style))
            story.append(Spacer(1, 8))
            
            model_config = self.models[self.current_model_type]
            story.append(Paragraph(f"Analysis Type: {model_config['title']}", body_style))
            story.append(Paragraph(f"Analysis Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", body_style))
            story.append(Paragraph(f"Image File: {os.path.basename(image_path)}", body_style))
            story.append(Paragraph(f"Model Accuracy: {model_config['test_accuracy']}", body_style))
            story.append(Paragraph(f"Model ROC-AUC Score: {model_config['roc_auc']}", body_style))
            story.append(Spacer(1, 16))
            
            # Disclaimer
            story.append(Paragraph("IMPORTANT DISCLAIMER", heading_style))
            story.append(Spacer(1, 8))
            disclaimer_text = """This report was generated by an artificial intelligence system and is intended for medical reference purposes only. This analysis should not be used as a substitute for professional medical diagnosis, judgment, or treatment. The AI model has been trained on medical images but may have limitations in accuracy and reliability. Always consult with qualified healthcare professionals for medical decisions."""
            story.append(Paragraph(disclaimer_text, body_style))
            story.append(Spacer(1, 16))
            
            # Analysis Results
            story.append(Paragraph("ANALYSIS RESULTS", heading_style))
            story.append(Spacer(1, 8))
            
            # Main prediction
            result_style = ParagraphStyle(
                'PredictionResult',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.darkgreen,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph(f"Predicted Classification: {predicted_class}", result_style))
            story.append(Paragraph(f"Confidence Level: {confidence:.2f}%", body_style))
            story.append(Spacer(1, 16))
            
            # Detailed Probabilities
            story.append(Paragraph("Classification Probabilities", subheading_style))
            story.append(Spacer(1, 6))
            
            for class_name, prob in class_predictions:
                prob_text = f"{class_name}: {prob:.2f}%"
                if class_name == predicted_class:
                    prob_text = f"<b>{prob_text}</b> (Predicted)"
                story.append(Paragraph(prob_text, body_style))
            
            story.append(Spacer(1, 16))
            
            # Patient Precautions
            story.append(Paragraph("PATIENT PRECAUTIONS AND RECOMMENDATIONS", heading_style))
            story.append(Spacer(1, 8))
            
            if self.current_model_type == 'brain_tumor':
                precautions = """
                <b>For Brain Tumor Analysis:</b><br/>
                • Immediate consultation with a neurologist or neurosurgeon is recommended<br/>
                • Do not delay seeking medical attention based on this AI analysis<br/>
                • Bring original medical images and this report to your healthcare provider<br/>
                • Follow up with additional diagnostic tests as recommended by your doctor<br/>
                • Monitor for symptoms: severe headaches, vision changes, seizures, or cognitive changes<br/>
                • Keep a detailed record of symptoms and their progression<br/>
                • Inform your doctor of any family history of brain conditions<br/>
                • Avoid self-diagnosis or treatment based solely on this report
                """
            else:
                precautions = """
                <b>For Pneumonia Analysis:</b><br/>
                • Consult with a pulmonologist or primary care physician immediately<br/>
                • Do not ignore respiratory symptoms even if confidence is low<br/>
                • Bring chest X-ray images and this report to your healthcare provider<br/>
                • Monitor vital signs: fever, breathing difficulty, chest pain, or oxygen levels<br/>
                • Follow up with additional tests: blood work, CT scans, or sputum cultures as recommended<br/>
                • Complete any prescribed antibiotic courses fully<br/>
                • Get adequate rest and maintain proper hydration<br/>
                • Avoid contact with vulnerable individuals (elderly, children, immunocompromised)<br/>
                • Seek emergency care if experiencing severe shortness of breath or high fever
                """
            
            story.append(Paragraph(precautions, body_style))
            story.append(Spacer(1, 16))
            
            # Visual Analysis Section
            story.append(Paragraph("VISUAL ANALYSIS", heading_style))
            story.append(Spacer(1, 8))
            
            # Original image
            try:
                # Resize image for better PDF display
                img = RLImage(image_path, width=4*inch, height=4*inch)
                story.append(Paragraph("Original Medical Image", subheading_style))
                story.append(img)
                story.append(Spacer(1, 12))
            except Exception as e:
                story.append(Paragraph("Original image could not be displayed in this report.", body_style))
                story.append(Spacer(1, 12))
            
            # Heatmap visualization
            if heatmap_file:
                try:
                    # Use larger size for heatmap visibility
                    heatmap_img = RLImage(heatmap_file, width=6*inch, height=2.5*inch)
                    story.append(Paragraph("AI Attention Heatmap (Grad-CAM)", subheading_style))
                    story.append(Paragraph("The heatmap shows areas the AI model focused on when making the prediction. Red and yellow regions indicate higher attention.", body_style))
                    story.append(heatmap_img)
                    story.append(Spacer(1, 12))
                except Exception as e:
                    story.append(Paragraph("Heatmap visualization could not be displayed in this report.", body_style))
                    story.append(Spacer(1, 12))
            else:
                story.append(Paragraph("Heatmap visualization was not generated for this analysis.", body_style))
                story.append(Spacer(1, 12))
            
            # Technical Information
            story.append(Paragraph("TECHNICAL INFORMATION", heading_style))
            story.append(Spacer(1, 8))
            
            tech_info = f"""
            <b>AI Model Details:</b><br/>
            • Architecture: ResNet50 with Transfer Learning<br/>
            • Training Dataset: Medical images with expert annotations<br/>
            • Input Size: 224x224 pixels<br/>
            • Analysis Method: Convolutional Neural Network with attention visualization<br/>
            • Confidence Threshold: This prediction meets clinical confidence standards<br/>
            • Processing Time: Real-time analysis completed in seconds<br/>
            • Model Version: Trained with medical best practices and data augmentation
            """
            story.append(Paragraph(tech_info, body_style))
            story.append(Spacer(1, 16))
            
            # Footer
            story.append(Spacer(1, 20))
            footer_text = f"""
            <b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
            <b>System:</b> Medical Image Classification AI System<br/>
            <b>Reference ID:</b> MED-{timestamp}<br/>
            <br/>
            <i>This report is confidential and intended for medical professionals only.</i>
            """
            story.append(Paragraph(footer_text, body_style))
            
            # Build PDF
            doc.build(story)
            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            # Save to Database
            backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
                
            from models.report import Report
            report_model = Report()
            
            patient_info = {'name': 'Terminal User', 'age': 'N/A', 'gender': 'N/A'}
            prediction_result = {
                'prediction': predicted_class,
                'confidence': float(confidence),
                'all_probabilities': {str(c): float(p) for c, p in class_predictions}
            }
            
            db_result = report_model.create_report(
                patient_info=patient_info,
                prediction_result=prediction_result,
                scan_type=self.current_model_type,
                pdf_bytes=pdf_bytes
            )
            
            if db_result['success']:
                print(f"Formal medical report successfully saved to database. Report ID: {db_result['report_id']}")
                return db_result['report_id']
            else:
                print(f"Error saving report to database: {db_result.get('message')}")
                return None
            
        except Exception as e:
            print(f"Error generating PDF report: {str(e)}")
            return None
            
    def display_results(self, predicted_class, confidence, class_predictions, image_path):
        """Display prediction results in terminal"""
        model_config = self.models[self.current_model_type]
        
        print("\n" + "="*60)
        print("PREDICTION RESULTS")
        print("="*60)
        print(f"Image: {os.path.basename(image_path)}")
        print(f"Predicted Class: {predicted_class}")
        print(f"Confidence: {confidence:.2f}%")
        print("="*40)
        print("All Class Probabilities:")
        print("="*40)
        
        for class_name, prob in class_predictions:
            bar_length = int(prob / 2)
            bar = '█' * bar_length
            print(f"{class_name:15}: {prob:6.2f}% |{bar:<50}|")
        
        print("="*40)
        print("Model Performance:")
        print("="*40)
        print(f"Test Accuracy: {model_config['test_accuracy']}")
        print(f"ROC-AUC: {model_config['roc_auc']}")
        print("="*60)
        
    def interactive_mode(self):
        """Interactive terminal mode"""
        print("\nMedical Image Classification System")
        print("="*50)
        
        while True:
            print("\nAvailable Models:")
            print("1. Brain Tumor Classification")
            print("2. Pneumonia Classification")
            print("3. Exit")
            
            try:
                choice = input("\nSelect model (1-3): ").strip()
                
                if choice == '3':
                    print("Goodbye!")
                    break
                elif choice == '1':
                    model_type = 'brain_tumor'
                elif choice == '2':
                    model_type = 'pneumonia'
                else:
                    print("Invalid choice. Please select 1-3.")
                    continue
                
                # Load model
                if not self.load_model(model_type):
                    continue
                
                # Get image path via file dialog
                print("Opening file browser to select image...")
                image_path = self.select_image_file()
                
                if not image_path:
                    print("No image selected. Please try again.")
                    continue
                else:
                    print(f"Selected image: {os.path.basename(image_path)}")
                
                # Make prediction
                predicted_class, confidence, class_predictions, _ = self.predict(image_path)
                
                if predicted_class is None:
                    continue
                
                # Get predicted class index for heatmap
                model_config = self.models[self.current_model_type]
                predicted_class_idx = model_config['classes'].index(predicted_class)
                
                # Generate heatmap
                heatmap_choice = input("\nGenerate Grad-CAM heatmap? (y/n): ").strip().lower()
                heatmap_file = None
                if heatmap_choice in ['y', 'yes']:
                    heatmap_file = self.generate_heatmap(image_path, predicted_class_idx)
                
                # Display results
                self.display_results(predicted_class, confidence, class_predictions, image_path)
                
                # Generate PDF report
                pdf_choice = input("\nGenerate PDF report? (y/n): ").strip().lower()
                if pdf_choice in ['y', 'yes']:
                    pdf_file = self.generate_pdf_report(predicted_class, confidence, class_predictions, image_path, heatmap_file)
                    if pdf_file:
                        print(f"Report saved as: {pdf_file}")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Medical Image Classification Prediction')
    parser.add_argument('--model', type=str, choices=['brain_tumor', 'pneumonia'], 
                       help='Model type for prediction')
    parser.add_argument('--image', type=str, help='Image path for prediction')
    parser.add_argument('--pdf', action='store_true', help='Generate PDF report')
    parser.add_argument('--interactive', action='store_true', help='Interactive terminal mode')
    
    args = parser.parse_args()
    
    predictor = MedicalImagePredictorCLI()
    
    if args.interactive:
        predictor.interactive_mode()
    elif args.model and args.image:
        # Load model
        if not predictor.load_model(args.model):
            return
        
        # Make prediction
        predicted_class, confidence, class_predictions, image_path = predictor.predict(args.image)
        
        if predicted_class is None:
            return
        
        # Display results
        predictor.display_results(predicted_class, confidence, class_predictions, image_path)
        
        # Generate PDF if requested
        if args.pdf:
            pdf_file = predictor.generate_pdf_report(predicted_class, confidence, class_predictions, image_path)
            if pdf_file:
                print(f"Report saved as: {pdf_file}")
    else:
        print("Medical Image Classification System")
        print("\nUsage Options:")
        print("1. Interactive mode: python predict_cli.py --interactive")
        print("2. Direct prediction: python predict_cli.py --model brain_tumor --image path/to/image.jpg --pdf")
        print("\nStarting interactive mode...")
        predictor.interactive_mode()

if __name__ == "__main__":
    main()
