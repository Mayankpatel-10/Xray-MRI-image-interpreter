# 🏥 MedScan AI - Medical Image Diagnosis System

![MedScan AI](screenshots/home-page.png)

## 📖 Overview
**MedScan AI** is an advanced, full-stack Artificial Intelligence web application designed to assist healthcare professionals in diagnosing medical images rapidly and accurately. It leverages deep learning—specifically **ResNet-50** architectures built with **PyTorch**—to provide automated screenings for Brain Tumors (from MRI/CT scans) and Pneumonia (from Chest X-rays). 

By combining rapid AI inference with explainable AI techniques (Grad-CAM heatmaps), MedScan AI delivers preliminary diagnostic predictions in seconds, complete with downloadable, professionally formatted PDF medical reports.

## 🎯 Problem Statement
Radiologists and healthcare clinics frequently face high workloads, leading to delayed reporting and patient anxiety. Furthermore, smaller clinics may lack immediate specialist availability. This project aims to bridge that gap by providing a reliable, fast, and explainable AI-based image analysis tool as a second opinion.

## 💡 Solution
MedScan AI uses state-of-the-art Deep Learning models to analyze medical images instantly. It integrates an intuitive React frontend, a robust Python Flask backend, and PyTorch ML models, along with automated PDF report generation and visual heatmaps to ensure diagnostic transparency.

---

## 🚀 Key Features
- **Intelligent Image Analysis**: Automated screening for Brain Tumors and Pneumonia using fine-tuned ResNet-50 models.
- **Explainable AI (Grad-CAM)**: Generates diagnostic overlay heatmaps to visually indicate which regions of the scan the AI focused on for its prediction.
- **Automated Medical Reports**: Generates professional, downloadable PDF reports containing patient data, diagnostic results, confidence scores, and heatmaps using ReportLab.
- **Secure Authentication**: Robust JWT-based user authentication and bcrypt password hashing.
- **Modern User Interface**: A responsive, dynamic, and beautiful UI built with React 19, Tailwind CSS, and Framer Motion.
- **History Tracking**: Secure storage of past diagnostic reports in MongoDB Atlas for easy retrieval.

---

## 🛠 Tech Stack

**Frontend**
- React 19 (Vite)
- Tailwind CSS
- Framer Motion & Lucide React
- React Router DOM
- Axios

**Backend**
- Python 3 & Flask
- Flask-JWT-Extended & Flask-CORS
- Bcrypt
- ReportLab (PDF Generation)

**AI / Machine Learning**
- PyTorch & TorchVision
- ResNet-50 CNN Architecture
- OpenCV & Pillow (Image Processing)
- Matplotlib (Grad-CAM Heatmap generation)

**Database**
- MongoDB Atlas (via PyMongo)

---

## 🏗️ System Architecture

```text
       [ User / Doctor ]
              │
              ▼
    [ React Frontend (Vite) ] ─── (Axios HTTP/REST)
              │
              ▼
   [ Python Flask Backend ] ─── (PyMongo) ─── [ MongoDB Atlas ]
              │
              ├── [ Auth Module (JWT) ]
              ├── [ PDF Generator (ReportLab) ]
              │
              ▼
 [ PyTorch Machine Learning ] ── [ Pre-trained ResNet-50 Models ]
      (Brain Tumor & Pneumonia Classifiers + Grad-CAM)
```

---

## 📸 Screenshots

**Home Page**
![Home Page](screenshots/home-page.png)

**Upload X-ray / MRI**
![Upload Page](screenshots/upload-page.png)

**Results Page & Explainable AI**
![Results Page](screenshots/results-page.png)

---

## 📂 Project Structure

```text
MedScan-AI/
│
├── backend/                  # Flask API server
│   ├── app.py                # Main backend entry point
│   ├── models/               # Database schemas/classes
│   ├── services/             # PDF generation and business logic
│   ├── reports/              # Generated PDF storage
│   └── requirements.txt      # Python dependencies
│
├── ui/                       # React Frontend
│   ├── src/                  # React components, contexts, services
│   ├── package.json          # Node dependencies
│   └── tailwind.config.js    # Tailwind styling config
│
├── ml/                       # Machine Learning Pipeline
│   ├── ml_models.py          # PyTorch model definitions
│   ├── train_unified.py      # Training scripts
│   ├── predict.py            # Inference and preprocessing logic
│   ├── *.pth                 # Pre-trained ResNet-50 weights
│   └── requirements.txt      # ML-specific dependencies
│
├── screenshots/              # UI demonstration images
├── data/                     # Local data storage
├── Dockerfile                # Docker container configuration
└── README.md                 # Project Documentation
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Mayankpatel-10/Xray-MRI-image-interpreter.git
cd Xray-MRI-image-interpreter
```

### 2. Backend Setup
```bash
cd backend
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env to add your MongoDB connection string and JWT Secret

# Run the Flask server
python app.py
```

### 3. Frontend Setup
```bash
cd ../ui
# Install dependencies
npm install

# Run the development server
npm run dev
```
*The frontend will typically run on `http://localhost:5173` and the backend on `http://localhost:5000`.*

---

## 🌟 Future Scope
- **Mobile Application**: Porting the React web app to React Native for mobile accessibility.
- **Multi-Language Support**: Expanding the UI and PDF reports for international clinics.
- **Model Optimization**: Utilizing ONNX or TensorRT to further decrease the <5s inference time.
- **Broader Disease Detection**: Adding models for Alzheimer's, bone fractures, and lung cancer.

---

## 🔒 Security Features
- **JWT Authentication**: Stateless and secure session management.
- **Role-Based Access Control**: Differentiating between standard users and system administrators.
- **Encrypted Passwords**: Bcrypt hashing for all stored credentials.

## 🤝 Contributors
| Name | Role |
| --- | --- |
| **Mayank Patel** | Lead AI/ML & Full-Stack Engineer |

## 📄 License
This project is licensed under the MIT License.

## 🙏 Acknowledgements
- **PyTorch** & **OpenCV** open-source communities.
- **ReportLab** for seamless PDF generation.
- Healthcare providers making anonymized datasets available for research.

## ⭐ Support
If you found this project useful or inspiring, please give it a star on GitHub!
