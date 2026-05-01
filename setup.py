#!/usr/bin/env python3
"""
Xray-MRI Image Interpreter - Setup Script
This script helps set up the complete project environment
"""

import os
import sys
import subprocess
import platform

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python():
    """Check if Python is installed"""
    print("Checking Python installation...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print("Python 3.8+ is required")
        return False

def check_node():
    """Check if Node.js is installed"""
    print("Checking Node.js installation...")
    success, output, error = run_command("node --version")
    if success:
        print(f"Node.js {output.strip()} - OK")
        return True
    else:
        print("Node.js is not installed or not in PATH")
        return False

def setup_backend():
    """Setup backend environment"""
    print("\n=== Setting up Backend ===")
    
    backend_dir = "backend"
    if not os.path.exists(backend_dir):
        print(f"Backend directory '{backend_dir}' not found!")
        return False
    
    print("Installing Python dependencies...")
    success, output, error = run_command("pip install -r requirements.txt", cwd=backend_dir)
    if success:
        print("Backend dependencies installed successfully")
        return True
    else:
        print(f"Failed to install backend dependencies: {error}")
        return False

def setup_frontend():
    """Setup frontend environment"""
    print("\n=== Setting up Frontend ===")
    
    ui_dir = "ui"
    if not os.path.exists(ui_dir):
        print(f"UI directory '{ui_dir}' not found!")
        return False
    
    print("Installing Node.js dependencies...")
    success, output, error = run_command("npm install", cwd=ui_dir)
    if success:
        print("Frontend dependencies installed successfully")
        return True
    else:
        print(f"Failed to install frontend dependencies: {error}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n=== Creating Directories ===")
    
    directories = [
        "backend/uploads",
        "backend/reports",
        "backend/services"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def print_instructions():
    """Print running instructions"""
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nTo run the project:")
    print("\n1. Backend (Terminal 1):")
    print("   cd backend")
    print("   python app.py")
    print("\n2. Frontend (Terminal 2):")
    print("   cd ui")
    print("   npm run dev")
    print("\n3. Access the application:")
    print("   Web Interface: http://localhost:5173")
    print("   Backend API: http://localhost:5000")
    print("   Health Check: http://localhost:5000/health")
    print("\n4. Test the backend (optional):")
    print("   cd backend")
    print("   python test_pdf.py")
    print("\n" + "="*60)

def main():
    """Main setup function"""
    print("Xray-MRI Image Interpreter - Setup Script")
    print("="*50)
    
    # Check prerequisites
    if not check_python():
        sys.exit(1)
    
    if not check_node():
        print("Please install Node.js from https://nodejs.org/")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup backend
    if not setup_backend():
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        sys.exit(1)
    
    # Print instructions
    print_instructions()

if __name__ == "__main__":
    main()
