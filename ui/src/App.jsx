import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './components/Toast';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import UploadCard from './components/UploadCard';
import About from './components/About';
import Footer from './components/Footer';
import { predictBrainTumor, predictPneumonia } from './services/api';
import { Brain, HeartPulse } from 'lucide-react';

function App() {
  const handleBrainPredict = async (file) => {
    const result = await predictBrainTumor(file);
    return result;
  };

  const handlePneumoniaPredict = async (file) => {
    const result = await predictPneumonia(file);
    return result;
  };

  return (
    <ThemeProvider>
      <ToastProvider>
        <div className="min-h-screen">
          <Navbar />
          <Hero />
          
          {/* Upload Section */}
          <section id="upload" className="py-20 px-4 bg-medical-50 dark:bg-gray-900">
            <div className="max-w-7xl mx-auto">
              <div className="text-center mb-12">
                <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
                  Upload Medical Images
                </h2>
                <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                  Select the type of analysis you need and upload your medical image for AI-powered diagnosis.
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
                <UploadCard
                  title="Brain Tumor Detection"
                  description="Upload CT Scan or Brain MRI"
                  icon={Brain}
                  accept=".jpg,.jpeg,.png,.dicom"
                  onPredict={handleBrainPredict}
                />
                <UploadCard
                  title="Pneumonia Detection"
                  description="Upload Chest X-Ray"
                  icon={HeartPulse}
                  accept=".jpg,.jpeg,.png"
                  onPredict={handlePneumoniaPredict}
                />
              </div>
            </div>
          </section>

          <About />
          <Footer />
        </div>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
