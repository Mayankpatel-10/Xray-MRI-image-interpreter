FROM python:3.10-slim

# Dependency install 
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Backend pip install
COPY backend/requirements.txt .

# Pip install for Cpu
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# All Backend Copy with ml Model
COPY backend/ ./backend/
COPY ml/ ./ml/

# Install curl and ca-certificates, download the real model files from GCS to overwrite the Git LFS pointer files, and cleanup
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -f -L -o ml/brain_tumor_resnet50_model.pth https://storage.googleapis.com/medscan-models-bucket/brain_tumor_resnet50_model.pth \
    && curl -f -L -o ml/pneumonia_resnet50_model.pth https://storage.googleapis.com/medscan-models-bucket/pneumonia_resnet50_model.pth \
    && apt-get purge -y --auto-remove curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

# Run flask
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
