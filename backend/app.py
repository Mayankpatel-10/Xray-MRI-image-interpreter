from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from bson.objectid import ObjectId
import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import numpy as np
import io
import base64
from datetime import datetime, timedelta
import warnings
import cv2
import matplotlib
matplotlib.use('Agg')  # Fix for Windows threading issues
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from services.pdf_generator import PDFGenerator
from models.user import User
from models.report import Report

# Add ML directory to path
ml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ml'))
if ml_path not in sys.path:
    sys.path.insert(0, ml_path)

# Import ML models directly
try:
    from ml_models import ResNetMedicalCNN, BrainTumorModel, PneumoniaModel
    print("Successfully imported ML models")
except ImportError as e:
    print(f"Error importing ML models: {e}")
    # Define fallback classes
    class ResNetMedicalCNN:
        def __init__(self, *args, **kwargs):
            pass
    
    class BrainTumorModel:
        def __init__(self, *args, **kwargs):
            pass
    
    class PneumoniaModel:
        def __init__(self, *args, **kwargs):
            pass

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'medscan-jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '24')))
jwt = JWTManager(app)

# Initialize User model
user_model = User()

# Initialize Report model
report_model = Report()

# Configuration
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(REPORTS_FOLDER):
    os.makedirs(REPORTS_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize PDF generator
pdf_generator = PDFGenerator()

# Grad-CAM class for heatmap generation
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

# Load models and transforms
brain_model = None
pneumonia_model = None
brain_transform = None
pneumonia_transform = None
load_error_message = None
model_details = {}

def load_models():
    """Load the ML models and transforms"""
    global brain_model, pneumonia_model, brain_transform, pneumonia_transform, load_error_message, model_details
    try:
        # Update paths to actual model files
        brain_model_path = os.path.join(ml_path, 'brain_tumor_resnet50_model.pth')
        pneumonia_model_path = os.path.join(ml_path, 'pneumonia_resnet50_model.pth')
        
        model_details['ml_path'] = ml_path
        if os.path.exists(ml_path):
            try:
                files = os.listdir(ml_path)
                model_details['ml_dir_contents'] = []
                for f in files:
                    fp = os.path.join(ml_path, f)
                    if os.path.isfile(fp):
                        model_details['ml_dir_contents'].append({
                            'name': f,
                            'size': os.path.getsize(fp)
                        })
                    else:
                        model_details['ml_dir_contents'].append({
                            'name': f,
                            'is_dir': True
                        })
            except Exception as le:
                model_details['list_error'] = str(le)
        else:
            model_details['ml_path_exists'] = False

        print(f"Looking for models at: {brain_model_path}")
        print(f"Looking for models at: {pneumonia_model_path}")
        
        # Load brain tumor model
        if os.path.exists(brain_model_path):
            print(f"Loading brain model from: {brain_model_path}")
            brain_tumor_model = BrainTumorModel()
            brain_model = brain_tumor_model.create_model()
            _, brain_transform = brain_tumor_model.get_transforms()
            
            # Load state dict
            checkpoint = torch.load(brain_model_path, map_location='cpu')
            brain_model.load_state_dict(checkpoint['model_state_dict'])
            brain_model.eval()
            globals()['brain_model'] = brain_model
            globals()['brain_transform'] = brain_transform
            print("Brain tumor model loaded successfully")
            print(f"Brain model classes: {brain_tumor_model.class_names}")
        else:
            print(f"Brain model not found at: {brain_model_path}")
            if os.path.exists(os.path.dirname(brain_model_path)):
                print("Available models:")
                print(os.listdir(os.path.dirname(brain_model_path)))
        
        # Load pneumonia model
        if os.path.exists(pneumonia_model_path):
            print(f"Loading pneumonia model from: {pneumonia_model_path}")
            pneumonia_model_obj = PneumoniaModel()
            pneumonia_model = pneumonia_model_obj.create_model()
            _, pneumonia_transform = pneumonia_model_obj.get_transforms()
            
            # Load state dict
            checkpoint = torch.load(pneumonia_model_path, map_location='cpu')
            pneumonia_model.load_state_dict(checkpoint['model_state_dict'])
            pneumonia_model.eval()
            globals()['pneumonia_model'] = pneumonia_model
            globals()['pneumonia_transform'] = pneumonia_transform
            print("Pneumonia model loaded successfully")
        else:
            print(f"Pneumonia model not found at: {pneumonia_model_path}")
            
    except Exception as e:
        print(f"Error loading models: {e}")
        import traceback
        load_error_message = f"{str(e)}\n{traceback.format_exc()}"

def preprocess_image(image_file, model_type='brain_tumor'):
    """Preprocess image for model prediction - matching predict.py exactly"""
    try:
        print(f"Processing image: {image_file.filename if hasattr(image_file, 'filename') else 'unknown'}")
        
        # CRITICAL FIX: Read image exactly like predict.py
        if hasattr(image_file, 'read'):  # Flask file object
            image_bytes = image_file.read()
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        else:  # File path
            image = Image.open(image_file).convert('RGB')
        
        print(f"Image loaded - mode: {image.mode}, size: {image.size}")
        
        # Debug image saving removed

        
        # Use same transforms as training (exact match to predict.py)
        if model_type == 'brain_tumor' and brain_transform:
            transform = brain_transform
        elif model_type == 'pneumonia' and pneumonia_transform:
            transform = pneumonia_transform
        else:
            # Fallback transforms
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        
        print(f"Using transform: {transform}")
        
        # Apply transform exactly like predict.py
        image_tensor = transform(image).unsqueeze(0)  # Add batch dimension
        print(f"Transformed tensor shape: {image_tensor.shape}, dtype: {image_tensor.dtype}")
        print(f"Tensor min/max: {image_tensor.min():.4f}/{image_tensor.max():.4f}")
        
        # CRITICAL: Device consistency
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        image_tensor = image_tensor.to(device)
        print(f"Tensor device: {image_tensor.device}")
        
        return image_tensor, image
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def generate_heatmap(model, image_tensor, original_image, predicted_class_idx):
    """Generate Grad-CAM heatmap"""
    try:
        print("Generating Grad-CAM heatmap...")
        
        # Initialize Grad-CAM
        grad_cam = GradCAM(model, 'backbone.layer4.2.conv3')
        
        # Generate CAM
        cam = grad_cam.generate_cam(image_tensor, predicted_class_idx)
        
        # Resize CAM to match image size
        original_size = original_image.size
        cam_resized = cv2.resize(cam, original_size)
        
        # Convert to numpy array
        img_array = np.array(original_image)
        
        # Create heatmap
        heatmap = cm.jet(cam_resized)[:, :, :3]  # Remove alpha channel
        heatmap = (heatmap * 255).astype(np.uint8)
        
        # Create overlay
        overlay = cv2.addWeighted(img_array, 0.6, heatmap, 0.4, 0)
        
        # Create visualization with original image and overlay image
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        
        # Original image
        axes[0].imshow(img_array)
        axes[0].set_title('Original Scan', fontsize=14, pad=10)
        axes[0].axis('off')
        
        # Overlay
        axes[1].imshow(overlay)
        axes[1].set_title('AI Diagnostic Overlay', fontsize=14, pad=10)
        axes[1].axis('off')
        
        plt.tight_layout()
        
        # Save heatmap to memory
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, dpi=150, bbox_inches='tight', format='png')
        plt.close()
        img_buffer.seek(0)
        
        # Convert to base64 for JSON response
        heatmap_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        print("Heatmap generated successfully")
        return heatmap_base64
        
    except Exception as e:
        print(f"Error generating heatmap: {e}")
        return None

def predict_brain_tumor(image_tensor, original_image):
    """Predict brain tumor from image tensor with heatmap"""
    try:
        if brain_model is None:
            return {
                'prediction': 'notumor',
                'confidence': 85.0,
                'message': 'Model not loaded - returning mock result',
                'heatmap': None,
                'all_probabilities': {}
            }
        
        with torch.no_grad():
            outputs = brain_model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            
            # Debug: Print raw outputs
            print(f"Raw model outputs: {outputs}")
            print(f"Probabilities: {probabilities}")
            print(f"Predicted index: {predicted.item()}, Confidence: {confidence.item()}")
            
            # Correct class names matching training
            classes = ["glioma", "meningioma", "notumor", "pituitary"]
            prediction = classes[predicted.item()]
            confidence_score = confidence.item() * 100
            predicted_class_idx = predicted.item()
            
            # Generate all probabilities
            all_probs = {}
            for i, class_name in enumerate(classes):
                all_probs[class_name] = round(probabilities[0][i].item() * 100, 2)
            
            print(f"All probabilities: {all_probs}")
            print(f"Final prediction: {prediction}")
            
            # Generate heatmap
            heatmap_base64 = generate_heatmap(brain_model, image_tensor, original_image, predicted_class_idx)
            
            return {
                'prediction': prediction,
                'confidence': round(confidence_score, 2),
                'heatmap': heatmap_base64,
                'all_probabilities': all_probs
            }
    except Exception as e:
        print(f"Error in brain tumor prediction: {e}")
        return {
            'prediction': 'Error',
            'confidence': 0,
            'error': str(e)
        }

def predict_pneumonia(image_tensor, original_image):
    """Predict pneumonia from image tensor with heatmap"""
    try:
        if pneumonia_model is None:
            return {
                'prediction': 'NORMAL',
                'confidence': 88.0,
                'message': 'Model not loaded - returning mock result',
                'heatmap': None,
                'all_probabilities': {}
            }
        
        with torch.no_grad():
            outputs = pneumonia_model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            
            # Correct class names matching training
            classes = ["NORMAL", "PNEUMONIA"]
            prediction = classes[predicted.item()]
            confidence_score = confidence.item() * 100
            predicted_class_idx = predicted.item()
            
            # Generate all probabilities
            all_probs = {}
            for i, class_name in enumerate(classes):
                all_probs[class_name] = round(probabilities[0][i].item() * 100, 2)
            
            # Generate heatmap
            heatmap_base64 = generate_heatmap(pneumonia_model, image_tensor, original_image, predicted_class_idx)

            return {
                'prediction': prediction,
                'confidence': round(confidence_score, 2),
                'heatmap': heatmap_base64,
                'all_probabilities': all_probs
            }
    except Exception as e:
        print(f"Error in pneumonia prediction: {e}")
        return {
            'prediction': 'Error',
            'confidence': 0,
            'error': str(e),
            'heatmap': None,
            'all_probabilities': {}
        }

@app.route('/')
def home():
    return jsonify({'message': 'MedScan AI Backend API is running'})

# Authentication Routes
@app.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Basic validation
        if len(name) < 2:
            return jsonify({'success': False, 'message': 'Name must be at least 2 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        # Create user
        result = user_model.create_user(name, email, password)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Registration successful',
                'user_id': result['user_id']
            }), 201
        else:
            return jsonify({'success': False, 'message': result['message']}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'Registration failed'}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Authenticate user
        result = user_model.authenticate_user(email, password)
        
        if result['success']:
            # Create access token
            access_token = create_access_token(identity=result['user']['id'])
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'access_token': access_token,
                'user': result['user']
            }), 200
        else:
            return jsonify({'success': False, 'message': result['message']}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'Login failed'}), 500

@app.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        current_user_id = get_jwt_identity()
        result = user_model.get_user_by_id(ObjectId(current_user_id))
        
        if result['success']:
            return jsonify({'success': True, 'user': result['user']}), 200
        else:
            return jsonify({'success': False, 'message': result['message']}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to get profile'}), 500

@app.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client-side token removal)"""
    return jsonify({'success': True, 'message': 'Logout successful'}), 200

@app.route('/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token"""
    try:
        current_user_id = get_jwt_identity()
        result = user_model.get_user_by_id(ObjectId(current_user_id))
        
        if result['success']:
            return jsonify({
                'success': True,
                'user': result['user'],
                'message': 'Token is valid'
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid token'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'Token verification failed'}), 401

@app.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all registered users (admin endpoint)"""
    try:
        current_user_id = get_jwt_identity()
        
        # For now, allow any authenticated user to view users
        # In production, you might want to add admin role check
        
        users = user_model.get_all_users()
        
        return jsonify({
            'success': True,
            'users': users,
            'total_count': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to fetch users'}), 500

@app.route('/admin/users/count', methods=['GET'])
@jwt_required()
def get_user_count():
    """Get total number of registered users"""
    try:
        current_user_id = get_jwt_identity()
        
        count = user_model.get_user_count()
        
        return jsonify({
            'success': True,
            'user_count': count
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to get user count'}), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'models_loaded': {
            'brain_tumor': brain_model is not None,
            'pneumonia': pneumonia_model is not None
        },
        'load_error': load_error_message,
        'model_details': model_details,
        'api_version': '2.1',
        'features': ['brain_tumor_detection', 'pneumonia_detection', 'pdf_reports', 'authentication']
    })

@app.route('/test/prediction', methods=['POST'])
def test_prediction():
    """Test endpoint for immediate response checking"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        scan_type = request.form.get('scan_type', 'brain')
        
        # Quick validation
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Process image
        image_tensor = preprocess_image(file)
        if image_tensor is None:
            return jsonify({'error': 'Failed to process image'}), 400
        
        # Make prediction based on scan type
        if scan_type == 'brain':
            result = predict_brain_tumor(image_tensor)
        else:
            result = predict_pneumonia(image_tensor)
        
        # Add test metadata
        result.update({
            'test_mode': True,
            'scan_type': scan_type,
            'timestamp': datetime.now().isoformat(),
            'processing_time': 'fast',
            'status': 'success' if 'error' not in result else 'error'
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'test_mode': True,
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/predict/brain', methods=['POST'])
@jwt_required()
def predict_brain():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'dcm'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Preprocess image
        image_tensor, original_image = preprocess_image(file, 'brain_tumor')
        if image_tensor is None:
            return jsonify({'error': 'Failed to process image'}), 400
        
        # Make prediction
        result = predict_brain_tumor(image_tensor, original_image)
        
        # Add metadata for better frontend integration
        result.update({
            'scan_type': 'brain',
            'timestamp': datetime.now().isoformat(),
            'status': 'success' if 'error' not in result else 'error',
            'image_processed': True
        })
        
        # Check if PDF report generation is requested
        generate_pdf = request.form.get('generate_pdf', 'false').lower() == 'true'
        
        if generate_pdf:
            # Get patient information from request
            patient_info = {
                'name': request.form.get('patient_name', 'Anonymous'),
                'age': request.form.get('patient_age', 'N/A'),
                'gender': request.form.get('patient_gender', 'N/A'),
                'symptoms': request.form.get('symptoms', ''),
                'doctor_name': request.form.get('doctor_name', 'N/A'),
                'notes': request.form.get('notes', ''),
                'scan_date': request.form.get('scan_date', datetime.now().strftime("%Y-%m-%d"))
            }
            
            # Get current user ID for report association
            current_user_id = None
            try:
                current_user_id = get_jwt_identity()
            except:
                pass
            
            # Create buffers for images to embed in PDF
            heatmap_buffer = None
            if result.get('heatmap'):
                import base64
                heatmap_buffer = io.BytesIO(base64.b64decode(result['heatmap']))
            
            original_image_buffer = io.BytesIO()
            original_image.save(original_image_buffer, format='PNG')
            original_image_buffer.seek(0)
            
            # Generate PDF report to bytes (for database storage)
            pdf_result = pdf_generator.generate_patient_report_to_bytes(
                patient_info=patient_info,
                prediction_result=result,
                scan_type='brain',
                heatmap_buffer=heatmap_buffer,
                original_image_buffer=original_image_buffer
            )
            
            if pdf_result['success']:
                # Save PDF to database
                db_result = report_model.create_report(
                    patient_info=patient_info,
                    prediction_result=result,
                    scan_type='brain',
                    pdf_bytes=pdf_result['pdf_bytes'],
                    user_id=current_user_id
                )
                
                if db_result['success']:
                    result['report_generated'] = True
                    result['report_id'] = db_result['report_id']
                    result['download_url'] = f"/download/report/{db_result['report_id']}"
                else:
                    result['report_generated'] = False
                    result['report_error'] = db_result['message']
            else:
                result['report_generated'] = False
                result['report_error'] = pdf_result['error']
        else:
            result['report_generated'] = False
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict/chest', methods=['POST'])
@jwt_required()
def predict_chest():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Preprocess image
        image_tensor, original_image = preprocess_image(file, 'pneumonia')
        if image_tensor is None:
            return jsonify({'error': 'Failed to process image'}), 400
        
        # Make prediction
        result = predict_pneumonia(image_tensor, original_image)
        
        # Add metadata for better frontend integration
        result.update({
            'scan_type': 'chest',
            'timestamp': datetime.now().isoformat(),
            'status': 'success' if 'error' not in result else 'error',
            'image_processed': True
        })
        
        # Check if PDF report generation is requested
        generate_pdf = request.form.get('generate_pdf', 'false').lower() == 'true'
        
        if generate_pdf:
            # Get patient information from request
            patient_info = {
                'name': request.form.get('patient_name', 'Anonymous'),
                'age': request.form.get('patient_age', 'N/A'),
                'gender': request.form.get('patient_gender', 'N/A'),
                'symptoms': request.form.get('symptoms', ''),
                'doctor_name': request.form.get('doctor_name', 'N/A'),
                'notes': request.form.get('notes', ''),
                'scan_date': request.form.get('scan_date', datetime.now().strftime("%Y-%m-%d"))
            }
            
            # Get current user ID for report association
            current_user_id = None
            try:
                current_user_id = get_jwt_identity()
            except:
                pass
            
            # Create buffers for images to embed in PDF
            heatmap_buffer = None
            if result.get('heatmap'):
                import base64
                heatmap_buffer = io.BytesIO(base64.b64decode(result['heatmap']))
            
            original_image_buffer = io.BytesIO()
            original_image.save(original_image_buffer, format='PNG')
            original_image_buffer.seek(0)
            
            # Generate PDF report to bytes (for database storage)
            pdf_result = pdf_generator.generate_patient_report_to_bytes(
                patient_info=patient_info,
                prediction_result=result,
                scan_type='chest',
                heatmap_buffer=heatmap_buffer,
                original_image_buffer=original_image_buffer
            )
            
            if pdf_result['success']:
                # Save PDF to database
                db_result = report_model.create_report(
                    patient_info=patient_info,
                    prediction_result=result,
                    scan_type='chest',
                    pdf_bytes=pdf_result['pdf_bytes'],
                    user_id=current_user_id
                )
                
                if db_result['success']:
                    result['report_generated'] = True
                    result['report_id'] = db_result['report_id']
                    result['download_url'] = f"/download/report/{db_result['report_id']}"
                else:
                    result['report_generated'] = False
                    result['report_error'] = db_result['message']
            else:
                result['report_generated'] = False
                result['report_error'] = pdf_result['error']
        else:
            result['report_generated'] = False
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate/report', methods=['POST'])
def generate_report():
    """Generate PDF report for patient and save to database"""
    try:
        # Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['patient_info', 'prediction_result', 'scan_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        patient_info = data['patient_info']
        prediction_result = data['prediction_result']
        scan_type = data['scan_type']
        
        # Get current user ID if available
        current_user_id = None
        try:
            current_user_id = get_jwt_identity()
        except:
            pass
        
        # Generate PDF report to bytes (for database storage)
        pdf_result = pdf_generator.generate_patient_report_to_bytes(
            patient_info=patient_info,
            prediction_result=prediction_result,
            scan_type=scan_type
        )
        
        if pdf_result['success']:
            # Save PDF to database
            db_result = report_model.create_report(
                patient_info=patient_info,
                prediction_result=prediction_result,
                scan_type=scan_type,
                pdf_bytes=pdf_result['pdf_bytes'],
                user_id=current_user_id
            )
            
            if db_result['success']:
                return jsonify({
                    'success': True,
                    'report_id': db_result['report_id'],
                    'download_url': f"/download/report/{db_result['report_id']}",
                    'message': 'Report generated successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': db_result['message']
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': pdf_result['error']
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/report/<report_id>', methods=['GET'])
def download_report(report_id):
    """Download PDF report from database"""
    try:
        # Validate report_id
        if not report_id:
            return jsonify({'error': 'Invalid report ID'}), 400
        
        # Get PDF from database
        pdf_result = report_model.get_pdf_by_report_id(report_id)
        
        if not pdf_result['success']:
            return jsonify({'error': pdf_result['message']}), 404
        
        # Create file-like object from bytes
        pdf_buffer = io.BytesIO(pdf_result['pdf_bytes'])
        
        # Send file
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=pdf_result['filename'],
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reports', methods=['GET'])
def list_reports():
    """List all available reports from database"""
    try:
        # Get reports from database
        reports = report_model.get_all_reports()
        
        # Format reports for response
        formatted_reports = []
        for report in reports:
            formatted_reports.append({
                'id': report['id'],
                'patient_name': report['patient_info'].get('name', 'N/A'),
                'scan_type': report['scan_type'],
                'prediction': report['prediction_result'].get('prediction', 'N/A'),
                'confidence': report['prediction_result'].get('confidence', 0),
                'created_at': report['created_at'].isoformat() if report['created_at'] else None,
                'download_url': f"/download/report/{report['id']}"
            })
        
        return jsonify({'reports': formatted_reports})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

# Load models immediately for production
load_models()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
