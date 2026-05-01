import requests
import json

# Test the backend API endpoints
def test_backend():
    base_url = "http://localhost:5000"
    
    print("Testing Backend API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health Check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health Check Error: {e}")
        return
    
    # Test PDF generation with sample data
    try:
        pdf_data = {
            "patient_info": {
                "name": "Test Patient",
                "age": "35",
                "gender": "Male",
                "scan_date": "2026-04-30"
            },
            "prediction_result": {
                "prediction": "Normal",
                "confidence": 92.5,
                "message": "No abnormalities detected"
            },
            "scan_type": "chest"
        }
        
        response = requests.post(f"{base_url}/generate/report", json=pdf_data)
        print(f"PDF Generation: {response.status_code} - {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"PDF Report Generated: {result['filename']}")
                print(f"Download URL: {base_url}{result['download_url']}")
        
    except Exception as e:
        print(f"PDF Generation Error: {e}")
    
    # Test list reports
    try:
        response = requests.get(f"{base_url}/reports")
        print(f"List Reports: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"List Reports Error: {e}")

if __name__ == "__main__":
    test_backend()
