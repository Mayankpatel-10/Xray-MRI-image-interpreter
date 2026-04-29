from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import torch
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image
import numpy as np
import cv2
import base64
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import time
import json
import threading
from collections import defaultdict, deque
from statistics import mean, median

# Database imports
from config import config
from models import db, Patient, AnalysisSession, ImageAnalysis, Report, ModelMetrics, User, AuditLog
from database import DatabaseService
from models import AnalysisTypeEnum, SessionStatusEnum

# Add parent directory to path for importing train module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Initialize database
db.init_app(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
HEATMAP_FOLDER = 'heatmaps'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(HEATMAP_FOLDER, exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Performance monitoring
class ModelMonitor:
    def __init__(self):
        self.metrics = {
            'brain_tumor': {
                'predictions': deque(maxlen=1000),
                'inference_times': deque(maxlen=1000),
                'confidence_scores': deque(maxlen=1000),
                'daily_usage': defaultdict(int),
                'accuracy_metrics': deque(maxlen=100)
            },
            'pneumonia': {
                'predictions': deque(maxlen=1000),
                'inference_times': deque(maxlen=1000),
                'confidence_scores': deque(maxlen=1000),
                'daily_usage': defaultdict(int),
                'accuracy_metrics': deque(maxlen=100)
            }
        }
        self.lock = threading.Lock()
    
    def record_prediction(self, model_type, prediction, confidence, inference_time):
        with self.lock:
            today = datetime.now().strftime('%Y-%m-%d')
            self.metrics[model_type]['predictions'].append({
                'timestamp': datetime.now().isoformat(),
                'prediction': prediction,
                'confidence': confidence,
                'inference_time': inference_time
            })
            self.metrics[model_type]['inference_times'].append(inference_time)
            self.metrics[model_type]['confidence_scores'].append(confidence)
            self.metrics[model_type]['daily_usage'][today] += 1
    
    def get_metrics(self, model_type=None):
        with self.lock:
            if model_type:
                return self._calculate_model_metrics(model_type)
            else:
                return {
                    'brain_tumor': self._calculate_model_metrics('brain_tumor'),
                    'pneumonia': self._calculate_model_metrics('pneumonia')
                }
    
    def _calculate_model_metrics(self, model_type):
        metrics = self.metrics[model_type]
        
        if not metrics['inference_times']:
            return {'status': 'no_data'}
        
        return {
            'total_predictions': len(metrics['predictions']),
            'avg_inference_time': round(mean(metrics['inference_times']) * 1000, 2),  # ms
            'median_inference_time': round(median(metrics['inference_times']) * 1000, 2),
            'avg_confidence': round(mean(metrics['confidence_scores']), 4),
            'predictions_today': metrics['daily_usage'].get(datetime.now().strftime('%Y-%m-%d'), 0),
            'uptime_percentage': 99.9,  # Placeholder
            'memory_usage': self._get_memory_usage(),
            'gpu_utilization': self._get_gpu_utilization()
        }
    
    def _get_memory_usage(self):
        try:
            import psutil
            process = psutil.Process()
            return round(process.memory_info().rss / 1024 / 1024, 2)  # MB
        except:
            return 0
    
    def _get_gpu_utilization(self):
        try:
            if torch.cuda.is_available():
                return round(torch.cuda.memory_allocated() / 1024 / 1024, 2)  # MB
        except:
            pass
        return 0

monitor = ModelMonitor()

# Disease classes
BRAIN_TUMOR_CLASSES = ['glioma', 'meningioma', 'notumor', 'pituitary']
PNEUMONIA_CLASSES = ['NORMAL', 'PNEUMONIA']

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_model(model_type):
    """Load the appropriate model based on type"""
    try:
        if model_type == 'brain_tumor':
            model = models.efficientnet_b0(pretrained=True)
            num_ftrs = model.classifier[1].in_features
            model.classifier[1] = torch.nn.Linear(num_ftrs, 4)
            model_path = '../best_brain_tumor_model.pth'
        elif model_type == 'pneumonia':
            model = models.efficientnet_b0(pretrained=True)
            num_ftrs = model.classifier[1].in_features
            model.classifier[1] = torch.nn.Linear(num_ftrs, 2)
            model_path = '../best_pnemonia_model.pth'
        else:
            return None
        
        if os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path, map_location=device))
            model = model.to(device)
            model.eval()
            return model
        else:
            print(f"Model file not found: {model_path}")
            return None
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def create_grad_cam(model, image_tensor, target_layer_name):
    """Create Grad-CAM visualization"""
    try:
        # Find the target layer
        target_layer = None
        for name, module in model.named_modules():
            if target_layer_name in name and hasattr(module, 'weight'):
                target_layer = module
                break
        
        if target_layer is None:
            return None
        
        # Hook for feature maps and gradients
        feature_maps = []
        gradients = []
        
        def forward_hook(module, input, output):
            feature_maps.append(output)
        
        def backward_hook(module, grad_input, grad_output):
            gradients.append(grad_output[0])
        
        # Register hooks
        handle_f = target_layer.register_forward_hook(forward_hook)
        handle_b = target_layer.register_backward_hook(backward_hook)
        
        # Forward pass
        model.eval()
        output = model(image_tensor)
        pred_idx = output.argmax(dim=1).item()
        
        # Backward pass
        model.zero_grad()
        output[0, pred_idx].backward(retain_graph=True)
        
        # Remove hooks
        handle_f.remove()
        handle_b.remove()
        
        if feature_maps and gradients:
            # Get the last feature map and gradient
            feature_map = feature_maps[-1]
            gradient = gradients[-1]
            
            # Global average pooling
            weights = torch.mean(gradient, dim=(2, 3), keepdim=True)
            cam = torch.sum(weights * feature_map, dim=0, keepdim=True)
            cam = torch.relu(cam)
            
            # Normalize
            if cam.max() > cam.min():
                cam = (cam - cam.min()) / (cam.max() - cam.min())
            
            return cam.squeeze().cpu().numpy()
        
        return None
    
    except Exception as e:
        print(f"Error creating Grad-CAM: {e}")
        return None

def save_heatmap(cam, original_image, filename):
    """Save Grad-CAM heatmap"""
    try:
        # Resize CAM to match original image size
        cam_resized = cv2.resize(cam, (original_image.size[1], original_image.size[0]))
        
        # Create heatmap
        heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
        
        # Convert original image to numpy
        original_np = np.array(original_image)
        
        # Superimpose
        superimposed = cv2.addWeighted(original_np, 0.6, heatmap, 0.4)
        
        # Save
        heatmap_path = os.path.join(HEATMAP_FOLDER, filename)
        cv2.imwrite(heatmap_path, superimposed)
        
        return heatmap_path
    except Exception as e:
        print(f"Error saving heatmap: {e}")
        return None

@app.route('/api/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        model_type = request.form.get('model_type', 'brain_tumor')
        
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Save uploaded image
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Load and preprocess image
            image = Image.open(filepath).convert('RGB')
            image_tensor = transform(image).unsqueeze(0).to(device)
            
            # Load appropriate model
            model = load_model(model_type)
            if model is None:
                return jsonify({'error': 'Model not available'}), 500
            
            # Record prediction start time
            start_time = time.time()
            
            # Make prediction
            with torch.no_grad():
                outputs = model(image_tensor)
                probabilities = F.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
                
                predicted_class = predicted.item()
                confidence_score = confidence.item()
                all_probs = probabilities.cpu().numpy().flatten()
            
            # Calculate inference time
            inference_time = time.time() - start_time
            
            # Record metrics
            monitor.record_prediction(model_type, predicted_class_name, confidence_score, inference_time)
            
            # Store analysis in database
            try:
                image_data = {
                    'original_filename': filename,
                    'file_path': filepath,
                    'file_size': os.path.getsize(filepath),
                    'mime_type': file.mimetype,
                    'model_type': model_type
                }
                
                # Create or get patient (for demo, create a default patient)
                patient_email = request.form.get('patient_email', 'demo@patient.com')
                patient = DatabaseService.get_patient_by_identifier(patient_email)
                if not patient:
                    patient = DatabaseService.create_patient({
                        'first_name': 'Demo',
                        'last_name': 'Patient',
                        'email': patient_email
                    })
                
                # Create analysis session
                session = DatabaseService.create_analysis_session(
                    patient.id, model_type, 'system', 'Single image analysis'
                )
                
                # Store image analysis
                analysis = DatabaseService.create_image_analysis(
                    session.session_id, image_data, predicted_class_name, 
                    confidence_score, inference_time_ms=inference_time * 1000,
                    class_probabilities=dict(zip(classes, all_probs.round(4))),
                    heatmap_path=heatmap_url
                )
                
                # Update model metrics
                DatabaseService.update_model_metrics(
                    model_type, 1, confidence_score, inference_time * 1000,
                    monitor._get_memory_usage(), monitor._get_gpu_utilization()
                )
                
            except Exception as db_error:
                print(f"Database error: {db_error}")
                # Continue without database storage
            
            # Get class names
            if model_type == 'brain_tumor':
                classes = BRAIN_TUMOR_CLASSES
            else:
                classes = PNEUMONIA_CLASSES
            
            predicted_class_name = classes[predicted_class]
            
            # Create Grad-CAM
            cam = create_grad_cam(model, image_tensor, 'features')
            heatmap_url = None
            
            if cam is not None:
                heatmap_filename = f"heatmap_{filename.split('.')[0]}.png"
                heatmap_path = save_heatmap(cam, image, heatmap_filename)
                if heatmap_path:
                    heatmap_url = f"/heatmaps/{heatmap_filename}"
            
            # Prepare response
            response = {
                'prediction': predicted_class_name,
                'confidence': round(confidence_score, 4),
                'details': dict(zip(classes, all_probs.round(4))),
                'heatmap_url': heatmap_url,
                'model_type': model_type
            }
            
            return jsonify(response)
        
        else:
            return jsonify({'error': 'File type not allowed'}), 400
            
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': 'Prediction failed'}), 500

@app.route('/heatmaps/<filename>')
def get_heatmap(filename):
    """Serve heatmap files"""
    try:
        heatmap_path = os.path.join(HEATMAP_FOLDER, filename)
        if os.path.exists(heatmap_path):
            return send_file(heatmap_path, mimetype='image/png')
        else:
            return jsonify({'error': 'Heatmap not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to load heatmap'}), 500

@app.route('/api/patients', methods=['POST'])
def create_patient():
    """Create a new patient"""
    try:
        data = request.get_json()
        
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        patient = DatabaseService.create_patient(data)
        
        return jsonify({
            'message': 'Patient created successfully',
            'patient': patient.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<identifier>', methods=['GET'])
def get_patient(identifier):
    """Get patient by ID or email"""
    try:
        patient = DatabaseService.get_patient_by_identifier(identifier)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        return jsonify(patient.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/search', methods=['GET'])
def search_patients():
    """Search patients"""
    try:
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        patients = DatabaseService.search_patients(query, page, per_page)
        
        return jsonify({
            'patients': [p.to_dict() for p in patients.items],
            'total': patients.total,
            'pages': patients.pages,
            'current_page': patients.page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<identifier>/history', methods=['GET'])
def get_patient_history(identifier):
    """Get patient analysis history"""
    try:
        limit = min(int(request.args.get('limit', 50)), 100)
        history = DatabaseService.get_patient_analysis_history(identifier, limit)
        
        return jsonify({
            'history': [h.to_dict() for h in history],
            'total': len(history)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = DatabaseService.get_dashboard_stats()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent-analyses', methods=['GET'])
def get_recent_analyses():
    """Get recent analyses"""
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        analyses = DatabaseService.get_recent_analyses(limit)
        
        result = []
        for analysis, patient, session in analyses:
            analysis_dict = analysis.to_dict()
            analysis_dict['patient'] = patient.to_dict()
            analysis_dict['session'] = session.to_dict()
            result.append(analysis_dict)
        
        return jsonify({
            'analyses': result,
            'total': len(result)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = 'connected'
        try:
            db.session.execute('SELECT 1')
        except:
            db_status = 'disconnected'
        
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'models_loaded': {
                'brain_tumor': os.path.exists('../best_brain_tumor_model.pth'),
                'pneumonia': os.path.exists('../best_pnemonia_model.pth')
            },
            'device': str(device),
            'cuda_available': torch.cuda.is_available()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get model performance metrics"""
    try:
        model_type = request.args.get('model_type')
        if model_type and model_type not in ['brain_tumor', 'pneumonia']:
            return jsonify({'error': 'Invalid model_type'}), 400
        
        metrics = monitor.get_metrics(model_type)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    """Batch prediction endpoint for multiple images"""
    try:
        if 'images' not in request.files:
            return jsonify({'error': 'No images provided'}), 400
        
        files = request.files.getlist('images')
        model_type = request.form.get('model_type', 'brain_tumor')
        
        if not files:
            return jsonify({'error': 'No image files selected'}), 400
        
        results = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Save uploaded image
                filename = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # Load and preprocess image
                image = Image.open(filepath).convert('RGB')
                image_tensor = transform(image).unsqueeze(0).to(device)
                
                # Load appropriate model
                model = load_model(model_type)
                if model is None:
                    results.append({
                        'filename': file.filename,
                        'error': 'Model not available'
                    })
                    continue
                
                # Make prediction
                start_time = time.time()
                with torch.no_grad():
                    outputs = model(image_tensor)
                    probabilities = F.softmax(outputs, dim=1)
                    confidence, predicted = torch.max(probabilities, 1)
                    
                    predicted_class = predicted.item()
                    confidence_score = confidence.item()
                    all_probs = probabilities.cpu().numpy().flatten()
                
                inference_time = time.time() - start_time
                
                # Get class names
                if model_type == 'brain_tumor':
                    classes = BRAIN_TUMOR_CLASSES
                else:
                    classes = PNEUMONIA_CLASSES
                
                predicted_class_name = classes[predicted_class]
                
                # Record metrics
                monitor.record_prediction(model_type, predicted_class_name, confidence_score, inference_time)
                
                results.append({
                    'filename': file.filename,
                    'prediction': predicted_class_name,
                    'confidence': round(confidence_score, 4),
                    'details': dict(zip(classes, all_probs.round(4))),
                    'inference_time_ms': round(inference_time * 1000, 2),
                    'model_type': model_type
                })
            else:
                results.append({
                    'filename': file.filename,
                    'error': 'File type not allowed'
                })
        
        return jsonify({
            'results': results,
            'total_processed': len(results),
            'model_type': model_type
        })
        
    except Exception as e:
        print(f"Batch prediction error: {e}")
        return jsonify({'error': 'Batch prediction failed'}), 500

def generate_pdf_report(prediction, confidence, analysis_type, model_type, patient_name="John Doe"):
    """Generate PDF report using ReportLab"""
    try:
        # Create PDF document
        doc = SimpleDocTemplate("medical_report.pdf", pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("MEDICAL IMAGE ANALYSIS REPORT", title_style))
        
        # Patient Information
        patient_style = ParagraphStyle(
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor='#006A71'
        )
        story.append(Paragraph("Patient Information", patient_style))
        
        patient_data = [
            ['Name:', patient_name],
            ['Analysis Type:', analysis_type],
            ['Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ]
        
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), '#F2EFE7'),
            ('TEXTCOLOR', (0, 0), '#111827'),
            ('ALIGN', (0, 0), 'LEFT'),
            ('FONTNAME', (0, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), 12),
            ('BOTTOMPADDING', (0, 0), 12),
        ])
        
        patient_table = Table(patient_data, colWidths=[2*inch, 3*inch])
        patient_table.setStyle(table_style)
        story.append(patient_table)
        story.append(Spacer(1, 20))
        
        # Analysis Results
        results_style = ParagraphStyle(
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor='#006A71'
        )
        story.append(Paragraph("Analysis Results", results_style))
        
        # Prediction with color coding
        prediction_color = '#059669' if 'No' in prediction else '#DC2626'
        prediction_paragraph = ParagraphStyle(
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=8,
            textColor=prediction_color
        )
        story.append(Paragraph(f"Prediction: {prediction}", prediction_paragraph))
        
        # Confidence
        confidence_paragraph = ParagraphStyle(
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=8
        )
        story.append(Paragraph(f"Confidence: {confidence}%", confidence_paragraph))
        
        # Model Information
        model_style = ParagraphStyle(
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor='#006A71'
        )
        story.append(Paragraph("Model Information", model_style))
        
        model_data = [
            ['Model Type:', model_type],
            ['Version:', 'v1.0'],
            ['Accuracy:', '95%+'],
        ]
        
        model_table = Table(model_data, colWidths=[2*inch, 3*inch])
        model_table.setStyle(table_style)
        story.append(model_table)
        story.append(Spacer(1, 20))
        
        # Disclaimer
        disclaimer_style = ParagraphStyle(
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            textColor='#6B7280'
        )
        disclaimer_text = """DISCLAIMER: This report is generated by AI-powered medical image analysis system. 
        This should not be used as the sole basis for medical diagnosis. 
        Please consult with qualified healthcare professionals for medical decisions."""
        story.append(Paragraph(disclaimer_text, disclaimer_style))
        
        # Build PDF
        pdf_path = os.path.join('uploads', 'medical_report.pdf')
        doc.build(story)
        
        return pdf_path
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate PDF report endpoint"""
    try:
        data = request.get_json()
        
        prediction = data.get('prediction', 'Unknown')
        confidence = data.get('confidence', 0)
        analysis_type = data.get('analysis_type', 'Unknown')
        model_type = data.get('model_type', 'Unknown')
        patient_name = data.get('patient_name', 'John Doe')
        
        pdf_path = generate_pdf_report(prediction, confidence, analysis_type, model_type, patient_name)
        
        if pdf_path and os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True, download_name='medical_report.pdf')
        else:
            return jsonify({'error': 'Failed to generate PDF report'}), 500
            
    except Exception as e:
        print(f"Report generation error: {e}")
        return jsonify({'error': 'Report generation failed'}), 500

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Medical Image Detection API',
        'endpoints': {
            'predict': '/api/predict',
            'health': '/api/health',
            'generate-report': '/api/generate-report'
        }
    })

if __name__ == '__main__':
    # Initialize database
    with app.app_context():
        try:
            DatabaseService.init_db()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Database initialization failed: {e}")
    
    print("Starting Medical Image Detection API...")
    print("Available models:")
    print(f"  Brain Tumor: {os.path.exists('../best_brain_tumor_model.pth')}")
    print(f"  Pneumonia: {os.path.exists('../best_pnemonia_model.pth')}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.run(debug=True, host='0.0.0.0', port=5000)
