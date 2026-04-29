# Xray-MRI Image Interpreter

I built this medical image analysis system that can detect brain tumors and pneumonia from medical images using deep learning models. The system is smart enough to know what type of image you're uploading, even if you accidentally select the wrong disease type.

## What This System Does

The application handles two main medical conditions:
- **Brain Tumor Detection**: Can identify glioma, meningioma, no tumor, and pituitary tumors from brain MRI scans
- **Pneumonia Detection**: Can detect normal vs pneumonia conditions from chest X-ray images
- **Smart Classification**: Automatically figures out whether your image is a brain scan or chest X-ray, then uses the right AI model

## The Cool Part - Smart Disease Detection

Here's what makes this system special: when you upload an image, it runs both AI models behind the scenes to determine what type of medical image you actually have. So if you accidentally select "Brain Tumor" but upload a chest X-ray, the system will catch this and let you know.

## How to Use It

Getting started is pretty straightforward:

1. **Install the requirements**: Run `pip install -r requirements.txt`
2. **Start the program**: Run `python predict.py`
3. **Choose what you want to analyze**: Pick Brain Tumor or Pneumonia from the menu
4. **Upload your medical image**: Select any JPG, PNG, or BMP file
5. **Get your results**: View the detailed analysis report

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
