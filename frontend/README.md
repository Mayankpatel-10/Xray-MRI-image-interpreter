# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

## MedScan AI - Medical Image Interpretation Frontend

A modern, user-friendly React.js frontend for AI-powered medical image diagnosis. This application allows users to upload medical images and get instant predictions for brain tumors (from MRI/CT scans) and pneumonia (from chest X-rays).

## 🎯 Project Overview

MedScan AI is a responsive web application that provides:
- **Brain Tumor Detection**: Analyzes CT scans and brain MRI images
- **Pneumonia Detection**: Analyzes chest X-ray images
- **Real-time Predictions**: Fast AI-powered analysis with confidence scores
- **Dark Mode Support**: Toggle between light and dark themes
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Professional UI**: Clean, hospital-grade interface with smooth animations

## ✨ Features

### UI Components
- **Navbar**: Logo, navigation links (Home, About, Contact), dark mode toggle, smooth scrolling
- **Hero Section**: Engaging headline, statistics (95%+ accuracy, <5s response time), call-to-action buttons
- **Upload Cards**: Drag & drop upload, image preview, file validation, progress bar
- **Result Display**: Prediction label, confidence percentage, color-coded results (green for normal, red for disease)
- **About Section**: Project purpose, AI explanation, disclaimer
- **Footer**: Copyright, social links, quick navigation

### Functional Features
- React functional components with hooks (useState, useEffect)
- Axios for API calls with error handling
- FormData for image uploads
- File validation (type and size)
- Toast notifications for user feedback
- Progress bar during analysis
- Theme context for dark mode
- Responsive design with Tailwind CSS

## 🛠 Tech Stack

- **React.js**: v19.2.0 - UI framework
- **Vite**: v7.2.2 - Build tool and dev server
- **Axios**: v1.7.9 - HTTP client for API calls
- **Tailwind CSS**: v3.4.17 - Utility-first CSS framework
- **Lucide React**: v0.468.0 - Icon library
- **PostCSS**: v8.4.49 - CSS processor
- **Autoprefixer**: v10.4.20 - CSS vendor prefixing

## 📁 Project Structure

```
ui/
├── public/
│   └── vite.svg
├── src/
│   ├── assets/
│   │   └── react.svg
│   ├── components/
│   │   ├── About.jsx        # About section with project info
│   │   ├── Footer.jsx       # Footer with social links
│   │   ├── Hero.jsx         # Hero section with CTA
│   │   ├── Navbar.jsx       # Navigation with dark mode
│   │   ├── Toast.jsx        # Toast notification component
│   │   └── UploadCard.jsx   # Reusable upload card with prediction
│   ├── context/
│   │   └── ThemeContext.jsx # Dark mode state management
│   ├── services/
│   │   └── api.js           # Axios API service
│   ├── App.jsx              # Main application component
│   ├── index.css            # Tailwind directives
│   └── main.jsx             # React entry point
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.js
└── vite.config.js
```

## 🚀 Setup Instructions

### Prerequisites
- Node.js (v18 or higher) - [Download here](https://nodejs.org/)
- npm (comes with Node.js) or yarn

### Step 1: Install Dependencies

Navigate to the project directory and install all required packages:

```bash
cd ui
npm install
```

This will install:
- React and React DOM
- Axios for API calls
- Tailwind CSS and its dependencies
- Lucide React for icons

### Step 2: Configure Backend URL

Create a `.env` file in the root of the `ui` directory to set your backend API URL:

```env
VITE_API_URL=http://localhost:5000
```

Replace `http://localhost:5000` with your actual backend URL.

### Step 3: Run Development Server

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Step 4: Build for Production

When ready to deploy:

```bash
npm run build
```

This creates an optimized production build in the `dist` folder.

To preview the production build:

```bash
npm run preview
```

## 🔌 Backend Connection Guide

### How Axios Connects Frontend to Backend

The API service (`src/services/api.js`) uses Axios to communicate with your backend:

1. **Axios Instance Configuration**:
   - Base URL is set from environment variable
   - Timeout set to 30 seconds
   - Default headers set for multipart/form-data (for image uploads)

2. **Request Interceptor**:
   - Can add authentication headers (commented out by default)
   - Useful for adding JWT tokens if you implement user authentication

3. **Response Interceptor**:
   - Handles errors consistently
   - Provides user-friendly error messages
   - Catches network errors, server errors, and request errors

4. **API Endpoints**:
   - `predictBrainTumor(file)`: POST to `/predict/brain`
   - `predictPneumonia(file)`: POST to `/predict/chest`
   - `healthCheck()`: GET to `/health` (optional, for backend status)

### Expected Backend API Format

Your backend should accept:

**Brain Tumor Prediction**:
```
POST /predict/brain
Content-Type: multipart/form-data
Body: file (image file)

Response:
{
  "prediction": "Tumor Detected" | "Normal",
  "confidence": 94.6
}
```

**Pneumonia Prediction**:
```
POST /predict/chest
Content-Type: multipart/form-data
Body: file (image file)

Response:
{
  "prediction": "Pneumonia" | "Normal",
  "confidence": 87.3
}
```

### Connecting to Different Backend Frameworks

**Flask Backend Example**:
```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route('/predict/brain', methods=['POST'])
def predict_brain():
    file = request.files['file']
    # Process image and get prediction
    result = your_model.predict(file)
    return jsonify({
        "prediction": result.label,
        "confidence": result.confidence
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**FastAPI Backend Example**:
```python
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float

@app.post("/predict/brain", response_model=PredictionResponse)
async def predict_brain(file: UploadFile = File(...)):
    # Process image and get prediction
    result = your_model.predict(file)
    return PredictionResponse(
        prediction=result.label,
        confidence=result.confidence
    )
```

## 🎨 How to Customize UI

### Changing Colors

Edit `tailwind.config.js` to customize the color scheme:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Your custom colors
        500: '#your-color',
      },
      medical: {
        // Medical-themed colors
        500: '#your-color',
      }
    }
  }
}
```

### Modifying Components

Each component is independent and can be modified:

1. **Navbar**: `src/components/Navbar.jsx` - Change navigation links, logo, or styling
2. **Hero**: `src/components/Hero.jsx` - Update headline, description, statistics
3. **UploadCard**: `src/components/UploadCard.jsx` - Modify upload behavior, validation rules
4. **About**: `src/components/About.jsx` - Update project information and features
5. **Footer**: `src/components/Footer.jsx` - Change social links and copyright

### Adding New Features

1. Create new component in `src/components/`
2. Import in `src/App.jsx`
3. Add to the layout

Example - Adding a Contact Form:
```jsx
// src/components/Contact.jsx
const Contact = () => {
  return (
    <section id="contact" className="py-20">
      {/* Your contact form */}
    </section>
  );
};

// In App.jsx
import Contact from './components/Contact';
// Add <Contact /> before <Footer />
```

## 🐛 Common Errors and Fixes

### Error: "Unknown at rule @tailwind"

**Cause**: Tailwind CSS not installed or not properly configured.

**Fix**:
```bash
npm install -D tailwindcss postcss autoprefixer
```

### Error: "Module not found: Can't resolve 'axios'"

**Cause**: Axios not installed.

**Fix**:
```bash
npm install axios
```

### Error: "Network Error" when uploading images

**Cause**: Backend not running or CORS not enabled.

**Fix**:
1. Ensure backend is running on the specified port
2. Enable CORS on your backend
3. Check that `VITE_API_URL` is correct in `.env` file

### Error: "File size must be less than 10MB"

**Cause**: Uploaded file exceeds size limit.

**Fix**: 
- Compress the image before uploading
- Or modify the size limit in `UploadCard.jsx`:
```javascript
if (selectedFile.size > 20 * 1024 * 1024) { // Change to 20MB
```

### Error: Dark mode not persisting

**Cause**: localStorage not working or theme context issue.

**Fix**: 
- Check browser localStorage is enabled
- Ensure ThemeProvider wraps the entire app in `App.jsx`

### Error: "Port 5173 already in use"

**Cause**: Another process is using the port.

**Fix**:
```bash
# Kill the process or use a different port
npm run dev -- --port 3000
```

## 🏆 Best Practices Used

### 1. Component Architecture
- **Functional Components**: All components are functional, not class-based
- **Reusable Components**: UploadCard is reusable for both brain and chest predictions
- **Props Validation**: Clear prop interfaces for component communication

### 2. State Management
- **React Hooks**: useState for local state, useEffect for side effects
- **Context API**: ThemeContext for global dark mode state
- **Lifting State Up**: State is managed at appropriate component levels

### 3. Code Organization
- **Separation of Concerns**: API logic separated into service layer
- **Folder Structure**: Logical grouping of components, context, services
- **Named Exports**: Consistent use of named exports for better tree-shaking

### 4. Error Handling
- **Try-Catch Blocks**: All async operations wrapped in error handling
- **User Feedback**: Toast notifications for success/error messages
- **Graceful Degradation**: UI remains functional even if features fail

### 5. Performance
- **Lazy Loading**: Components load only when needed
- **Optimized Images**: Image previews use FileReader for client-side preview
- **Debouncing**: Not implemented but recommended for search/filter inputs

### 6. Accessibility
- **Semantic HTML**: Proper use of section, nav, footer elements
- **ARIA Labels**: Buttons have aria-labels for screen readers
- **Keyboard Navigation**: All interactive elements are keyboard accessible

### 7. Security
- **File Validation**: Client-side validation for file type and size
- **Environment Variables**: Sensitive data in .env files
- **Input Sanitization**: File inputs are handled securely

### 8. Styling
- **Tailwind CSS**: Utility-first approach for consistent styling
- **Dark Mode**: Built-in dark mode support with smooth transitions
- **Responsive Design**: Mobile-first approach with breakpoints
- **Custom Animations**: Smooth fade-in and slide-up animations

## 🔮 Future Improvements

### 1. User Authentication
- Login/registration system
- User profiles
- Prediction history
- Session management

### 2. Enhanced Features
- Batch image upload
- Comparison mode (multiple images)
- Download prediction reports as PDF
- Email notification of results
- Image annotation/markup tools

### 3. Advanced UI/UX
- Loading skeletons
- Virtual scrolling for large lists
- Image zoom and pan
- Before/after comparison slider
- Advanced filtering and search

### 4. Backend Integration
- WebSocket for real-time progress
- Queue system for batch processing
- Caching for repeated predictions
- Rate limiting

### 5. Analytics
- Usage statistics dashboard
- Prediction accuracy tracking
- User behavior analytics
- Performance monitoring

### 6. Deployment
- Docker containerization
- CI/CD pipeline setup
- Cloud deployment (AWS, GCP, Azure)
- CDN for static assets
- Database integration for history

### 7. Accessibility
- Full WCAG 2.1 compliance
- Screen reader optimization
- Keyboard shortcuts
- High contrast mode

### 8. Testing
- Unit tests with Jest
- Integration tests
- E2E tests with Playwright
- Visual regression tests

## 📝 License

This project is for educational and research purposes. Please ensure compliance with medical data regulations (HIPAA, GDPR) when deploying with real patient data.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Contact: contact@medscan.ai

---

**Built with ❤️ using React and Tailwind CSS**
