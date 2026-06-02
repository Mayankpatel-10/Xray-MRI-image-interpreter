import { useState } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './components/Toast';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import UploadCard from './components/UploadCard';
import About from './components/About';
import Footer from './components/Footer';
import Login from './components/Login';
import Signup from './components/Signup';
import History from './components/History';
import { predictBrainTumor, predictPneumonia } from './services/api';
import { Brain, HeartPulse } from 'lucide-react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
  const [selectedScanType, setSelectedScanType] = useState('brain');

  const handleBrainPredict = async (file) => {
    const result = await predictBrainTumor(file);
    return result;
  };

  const handlePneumoniaPredict = async (file) => {
    const result = await predictPneumonia(file);
    return result;
  };

  return (
    <Router>
      <ThemeProvider>
        <ToastProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/history" element={<History />} />
            <Route path="/" element={
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

                    {/* Scan Type Toggle / Selector */}
                    <div className="flex justify-center mb-10 px-4 w-full">
                      <div className="flex flex-col sm:flex-row p-1.5 bg-gray-100 dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 w-full sm:w-auto max-w-md gap-2 sm:gap-0">
                        <button
                          onClick={() => setSelectedScanType('brain')}
                          className={`flex items-center justify-center gap-2 px-4 sm:px-6 py-3 sm:py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all duration-300 w-full sm:w-auto ${
                            selectedScanType === 'brain'
                              ? 'bg-medical-600 text-white shadow-md'
                              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                          }`}
                        >
                          <Brain className="w-4 h-4 shrink-0" />
                          Brain Tumor Detection
                        </button>
                        <button
                          onClick={() => setSelectedScanType('pneumonia')}
                          className={`flex items-center justify-center gap-2 px-4 sm:px-6 py-3 sm:py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all duration-300 w-full sm:w-auto ${
                            selectedScanType === 'pneumonia'
                              ? 'bg-medical-600 text-white shadow-md'
                              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                          }`}
                        >
                          <HeartPulse className="w-4 h-4 shrink-0" />
                          Pneumonia Detection
                        </button>
                      </div>
                    </div>

                    <div className="max-w-2xl mx-auto">
                      {selectedScanType === 'brain' ? (
                        <UploadCard
                          title="Brain Tumor Detection"
                          description="Upload CT Scan or Brain MRI"
                          icon={Brain}
                          accept=".jpg,.jpeg,.png,.dicom"
                          onPredict={handleBrainPredict}
                        />
                      ) : (
                        <UploadCard
                          title="Pneumonia Detection"
                          description="Upload Chest X-Ray"
                          icon={HeartPulse}
                          accept=".jpg,.jpeg,.png"
                          onPredict={handlePneumoniaPredict}
                        />
                      )}
                    </div>
                  </div>
                </section>

                <About />
                <Footer />
              </div>
            } />
          </Routes>
        </ToastProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;
