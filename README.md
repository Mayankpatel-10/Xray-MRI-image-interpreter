# Xray-MRI Image Interpreter

A comprehensive medical image analysis system that can detect brain tumors and pneumonia from medical images using deep learning models. The system includes both a web interface and command-line tools, with smart classification that automatically detects image types.

## Project Structure

```
EL-Project/
│
├── backend/                 # Flask API server
│   ├── app.py              # Main Flask application
│   ├── routes/             # API route handlers
│   ├── services/           # Business logic services
│   ├── models/             # ML models loading logic
│   ├── utils/              # Utility functions
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
│
├── frontend/               # React.js web application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── ml/                     # Machine learning components
│   ├── train.py           # Model training script
│   ├── predict.py         # Command-line prediction
│   ├── models/            # Trained model files
│   │   ├── best_brain_tumor_model.pth
│   │   └── best_pnemonia_model.pth
│   ├── outputs/           # Training outputs
│   │   ├── confusion_matrix.png
│   │   └── training_history.png
│   └── requirements.txt   # ML dependencies
│
├── data/                   # Training datasets
│   ├── brain_tumor/
│   └── pneumonia/
│
├── README.md
└── .gitignore
```

## What This System Does

The application handles two main medical conditions:
- **Brain Tumor Detection**: Can identify glioma, meningioma, no tumor, and pituitary tumors from brain MRI scans
- **Pneumonia Detection**: Can detect normal vs pneumonia conditions from chest X-ray images
- **Smart Classification**: Automatically figures out whether your image is a brain scan or chest X-ray, then uses the right AI model

## Getting Started

### Web Application (Recommended)

1. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   python app.py
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access the application** at `http://localhost:5173`

### Command Line Interface

1. **Install ML requirements**:
   ```bash
   cd ml
   pip install -r requirements.txt
   ```

2. **Run predictions**:
   ```bash
   python predict.py
   ```

## What You'll See

The system gives you a comprehensive 4-panel report:
- Your original medical image
- The main prediction with confidence percentage
- A heat map showing exactly what the AI was looking at
- Detailed breakdown of all possible conditions

## The Technology Behind It

I used two separate EfficientNet-B0 models:
- One trained specifically on brain MRI scans for tumor detection
- Another trained on chest X-rays for pneumonia detection
- Both models achieve 95%+ accuracy on their respective tasks

## What You Need

Just two model files:
- `best_brain_tumor_model.pth` - For brain tumor analysis
- `best_pnemonia_model.pth` - For pneumonia analysis

## Performance Numbers

Based on my testing:
- Brain Tumor Detection: About 95% accurate
- Pneumonia Detection: About 96% accurate

## Important - Please Read

This tool was built for educational purposes to help understand how AI can assist in medical image analysis. It should never be used as the only basis for medical decisions. Always talk to qualified healthcare professionals for any medical concerns.

## What's New

**Version 2.0** - I just added the smart disease classification feature that prevents the system from giving wrong results when users accidentally select the wrong disease type. The system now automatically detects what type of medical image you have and uses the correct AI model.
