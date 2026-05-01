# Medical Image Analysis System

An AI-powered system that analyzes medical images to detect brain tumors and pneumonia. Uses deep learning models to provide accurate predictions with professional PDF reports.

## What It Does

- **Brain Tumor Detection**: Identifies glioma, meningioma, no tumor, and pituitary tumors from MRI scans
- **Pneumonia Detection**: Detects normal vs pneumonia conditions from chest X-rays
- **Smart Analysis**: Automatically detects image type and uses the correct AI model
- **PDF Reports**: Generates professional medical reports for download

## Getting Started

## How to Run

### **Step 1: Backend Setup**
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Backend runs on: `http://localhost:5000`

### **Step 2: Frontend Setup**
```bash
cd ui
npm install
npm run dev
```
Frontend runs on: `http://localhost:5173`

### **Step 3: Use the App**
Open your browser and go to `http://localhost:5173`

## How It Works

1. **Upload Image** - Choose brain MRI or chest X-ray
2. **AI Analysis** - System analyzes and predicts
3. **Get Results** - See prediction with confidence score
4. **Download Report** - Get professional PDF report (optional)

## Features

- **Smart Detection** - Automatically identifies image type
- **High Accuracy** - 95%+ accuracy on both conditions
- **PDF Reports** - Professional medical reports
- **Easy Interface** - Simple drag-and-drop upload
- **Real-time Results** - Fast predictions with confidence scores

## API Endpoints

- `POST /predict/brain` - Analyze brain MRI
- `POST /predict/chest` - Analyze chest X-ray
- `GET /health` - Check system status
- `POST /test/prediction` - Quick testing endpoint

## Command Line Tool

For advanced users:
```bash
cd ml
pip install -r requirements.txt
python predict.py
```

## Technology

- **Models**: EfficientNet-B0 for both brain and chest analysis
- **Backend**: Flask with PyTorch
- **Frontend**: React with Tailwind CSS
- **Reports**: Professional PDF generation

## Important Notice

This tool is for educational purposes only. Always consult qualified healthcare professionals for medical decisions.

## Requirements

- Python 3.8+
- Node.js 16+
- Two model files in `/ml` folder:
  - `best_brain_tumor_model.pth`
  - `best_pneumonia_model.pth`
