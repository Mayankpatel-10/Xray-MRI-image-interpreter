import { ArrowRight, Brain, HeartPulse } from 'lucide-react';

const Hero = () => {
  const scrollToUpload = () => {
    const element = document.getElementById('upload');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section id="home" className="min-h-screen flex items-center justify-center pt-16 px-4 bg-medical-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="space-y-8 animate-slide-up">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-medical-100 dark:bg-medical-900/30 text-medical-700 dark:text-medical-300 text-sm font-medium">
              <HeartPulse className="w-4 h-4" />
              AI-Powered Medical Diagnosis
            </div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white leading-tight">
              AI Powered{' '}
              <span className="text-medical-600 dark:text-medical-400">
                Medical Image
              </span>{' '}
              Diagnosis
            </h1>
            
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-xl">
              Upload your medical images and get instant AI-powered predictions. 
              Detect brain tumors from MRI/CT scans and pneumonia from chest X-rays with our advanced deep learning models.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={scrollToUpload}
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-medical-600 text-white font-semibold rounded-lg hover:bg-medical-700 transition-all shadow-lg shadow-medical-600/20 hover:shadow-xl transform hover:-translate-y-1"
              >
                Get Started
                <ArrowRight className="w-5 h-5" />
              </button>
              <button
                onClick={() => document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' })}
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 font-semibold rounded-lg border-2 border-gray-200 dark:border-gray-700 hover:border-medical-500 dark:hover:border-medical-400 transition-all"
              >
                Learn More
              </button>
            </div>
            
            <div className="grid grid-cols-3 gap-2 sm:flex sm:items-center sm:gap-8 pt-4 max-w-md mx-auto lg:mx-0">
              <div className="text-center">
                <div className="text-2xl sm:text-3xl font-bold text-medical-600 dark:text-medical-400">95%+</div>
                <div className="text-[11px] sm:text-sm text-gray-600 dark:text-gray-400">Accuracy</div>
              </div>
              <div className="hidden sm:block w-px h-12 bg-gray-300 dark:bg-gray-600"></div>
              <div className="text-center">
                <div className="text-2xl sm:text-3xl font-bold text-medical-600 dark:text-medical-400">&lt;5s</div>
                <div className="text-[11px] sm:text-sm text-gray-600 dark:text-gray-400">Response Time</div>
              </div>
              <div className="hidden sm:block w-px h-12 bg-gray-300 dark:bg-gray-600"></div>
              <div className="text-center">
                <div className="text-2xl sm:text-3xl font-bold text-medical-600 dark:text-medical-400">24/7</div>
                <div className="text-[11px] sm:text-sm text-gray-600 dark:text-gray-400">Available</div>
              </div>
            </div>
          </div>
          
          {/* Right Content - Illustration */}
          <div className="relative animate-fade-in">
            <div className="relative z-10 bg-white/70 backdrop-blur-lg rounded-3xl shadow-2xl p-8 border border-white/50">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="aspect-square rounded-xl bg-medical-100 dark:from-medical-900/50 flex items-center justify-center">
                    <Brain className="w-24 h-24 text-medical-600 dark:text-medical-400" />
                  </div>
                  <div className="text-center">
                    <h3 className="font-semibold text-gray-900 dark:text-white">Brain Tumor</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">MRI/CT Scan Analysis</p>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="aspect-square rounded-xl bg-primary-100 dark:from-primary-900/50 flex items-center justify-center">
                    <HeartPulse className="w-24 h-24 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div className="text-center">
                    <h3 className="font-semibold text-gray-900 dark:text-white">Pneumonia</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Chest X-Ray Analysis</p>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Decorative elements */}
            <div className="absolute -top-12 -right-12 w-40 h-40 bg-[#22D3EE]/25 rounded-full blur-3xl"></div>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-60 h-60 bg-[#14B8A6]/15 rounded-full blur-3xl"></div>
            <div className="absolute -bottom-12 -left-12 w-48 h-48 bg-[#0F4C81]/20 rounded-full blur-3xl"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
