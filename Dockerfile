FROM python:3.10-slim

# Install system dependencies required for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements from backend
COPY backend/requirements.txt .

# Install dependencies using CPU-only PyTorch to save memory
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Copy backend and ml folders
COPY backend/ ./backend/
COPY ml/ ./ml/

# Install curl, download the real model files from GCS to overwrite the Git LFS pointer files, and cleanup
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && curl -L -o ml/brain_tumor_resnet50_model.pth https://storage.googleapis.com/medscan-models-bucket/brain_tumor_resnet50_model.pth \
    && curl -L -o ml/pneumonia_resnet50_model.pth https://storage.googleapis.com/medscan-models-bucket/pneumonia_resnet50_model.pth \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

# Start the Flask app using gunicorn on the port specified by Cloud Run
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
