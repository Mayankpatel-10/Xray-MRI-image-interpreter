import { useState, useRef } from 'react';
import { Upload, X, Image as ImageIcon, Loader2, Download, User, Calendar, Activity, Stethoscope, ClipboardList } from 'lucide-react';

const UploadCard = ({ title, description, icon: Icon, accept, onPredict, apiEndpoint }) => {
  const [currentStep, setCurrentStep] = useState(1); // 1: Patient Info, 2: Upload
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);
  const [result, setResult] = useState(null);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef(null);

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile) return;
    const validTypes = accept.split(',').map(type => type.trim());
    const fileExtension = `.${selectedFile.name.split('.').pop().toLowerCase()}`;
    if (!validTypes.includes(fileExtension) && !validTypes.includes(selectedFile.type)) {
      alert(`Please upload a valid ${title.toLowerCase()} image file`);
      return;
    }
    setFile(selectedFile);
    setResult(null);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(selectedFile);
  };

  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = (e) => { e.preventDefault(); setIsDragging(false); };
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files[0]);
  };
  const handleInputChange = (e) => handleFileSelect(e.target.files[0]);
  const handleRemoveFile = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setProgress(0);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const [patientDetails, setPatientDetails] = useState({
    name: '',
    age: '',
    gender: '',
    symptoms: '',
    doctorName: '',
    notes: ''
  });

  const handlePatientDetailChange = (e) => {
    const { name, value } = e.target;
    setPatientDetails(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const isPatientInfoValid = () => {
    return (
      patientDetails.name.trim().length >= 2 &&
      patientDetails.age > 0 &&
      patientDetails.gender !== ''
    );
  };

  const handleNextStep = () => {
    if (isPatientInfoValid()) {
      setCurrentStep(2);
    }
  };

  const handlePrevStep = () => {
    setCurrentStep(1);
    setResult(null);
  };

  const handlePredict = async () => {
    if (!file || !isPatientInfoValid()) return;

    setIsPredicting(true);
    setProgress(0);

    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 200);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('patient_name', patientDetails.name);
      formData.append('patient_age', patientDetails.age);
      formData.append('patient_gender', patientDetails.gender);
      formData.append('symptoms', patientDetails.symptoms);
      formData.append('doctor_name', patientDetails.doctorName);
      formData.append('notes', patientDetails.notes);
      formData.append('generate_pdf', 'true');

      const response = await onPredict(formData);
      setProgress(100);
      setResult(response);
    } catch (error) {
      console.error('Prediction error:', error);
      setResult({
        prediction: 'Error',
        confidence: 0,
        error: error.message || 'Failed to get prediction'
      });
    } finally {
      clearInterval(progressInterval);
      setIsPredicting(false);
    }
  };

  const isDiseaseDetected = (() => {
    if (!result || !result.prediction) return false;
    const pred = result.prediction.toLowerCase();
    if (pred.includes('no tumor') || pred.includes('notumor') || pred.includes('no_tumor') || pred.includes('normal')) {
      return false;
    }
    return (
      pred.includes('tumor') ||
      pred.includes('pneumonia') ||
      pred.includes('positive') ||
      pred.includes('glioma') ||
      pred.includes('meningioma') ||
      pred.includes('pituitary')
    );
  })();

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden transition-all duration-500">
      <div className="p-0">
        {/* Step Indicator Header */}
        <div className="flex border-b border-gray-100 dark:border-gray-700">
          <button 
            onClick={() => setCurrentStep(1)}
            className={`flex-1 py-4 text-sm font-semibold flex items-center justify-center gap-2 transition-all ${
              currentStep === 1 
                ? 'text-medical-600 dark:text-medical-400 bg-medical-50/50 dark:bg-medical-900/10' 
                : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
            }`}
          >
            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
              currentStep === 1 ? 'bg-medical-600 text-white' : 'bg-gray-200 dark:bg-gray-700'
            }`}>1</span>
            Patient Profile
          </button>
          <button 
            onClick={() => isPatientInfoValid() && setCurrentStep(2)}
            disabled={!isPatientInfoValid()}
            className={`flex-1 py-4 text-sm font-semibold flex items-center justify-center gap-2 transition-all ${
              currentStep === 2 
                ? 'text-medical-600 dark:text-medical-400 bg-medical-50/50 dark:bg-medical-900/10' 
                : 'text-gray-400 disabled:opacity-50'
            }`}
          >
            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
              currentStep === 2 ? 'bg-medical-600 text-white' : 'bg-gray-200 dark:bg-gray-700'
            }`}>2</span>
            Diagnostic Imaging
          </button>
        </div>

        <div className="p-6">
          {/* Main Content Areas */}
          {currentStep === 1 ? (
            <div className="space-y-6 animate-in fade-in slide-in-from-left-4 duration-300">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-medical-100 dark:bg-medical-900/50">
                  <Icon className="w-6 h-6 text-medical-600 dark:text-medical-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">{title}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Step 1: Patient Information Profile</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Patient Name</label>
                  <input
                    type="text"
                    name="name"
                    value={patientDetails.name}
                    onChange={handlePatientDetailChange}
                    placeholder="Enter full name"
                    className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-900/30 border border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-medical-500 outline-none transition-all dark:text-white"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Age</label>
                    <input
                      type="number"
                      name="age"
                      value={patientDetails.age}
                      onChange={handlePatientDetailChange}
                      placeholder="Age"
                      className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-900/30 border border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-medical-500 outline-none transition-all dark:text-white"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Gender</label>
                    <select
                      name="gender"
                      value={patientDetails.gender}
                      onChange={handlePatientDetailChange}
                      className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-900/30 border border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-medical-500 outline-none transition-all dark:text-white"
                    >
                      <option value="">Select</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Referring Doctor</label>
                  <input
                    type="text"
                    name="doctorName"
                    value={patientDetails.doctorName}
                    onChange={handlePatientDetailChange}
                    placeholder="Dr. Name (Optional)"
                    className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-900/30 border border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-medical-500 outline-none transition-all dark:text-white"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Primary Symptoms</label>
                  <input
                    type="text"
                    name="symptoms"
                    value={patientDetails.symptoms}
                    onChange={handlePatientDetailChange}
                    placeholder="e.g. Headache, Cough"
                    className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-900/30 border border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-medical-500 outline-none transition-all dark:text-white"
                  />
                </div>
              </div>
              
              <button
                onClick={handleNextStep}
                disabled={!isPatientInfoValid()}
                className="w-full py-4 bg-medical-600 text-white font-bold rounded-xl hover:bg-medical-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-medical-600/20 flex items-center justify-center gap-2"
              >
                Proceed to Image Upload
                <X className="w-4 h-4 rotate-45" />
              </button>
            </div>
          ) : (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-medical-100 dark:bg-medical-900/50">
                    <Icon className="w-6 h-6 text-medical-600 dark:text-medical-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">{title}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{description}</p>
                  </div>
                </div>
                <button 
                  onClick={handlePrevStep}
                  className="text-sm text-medical-600 dark:text-medical-400 font-semibold hover:underline"
                >
                  Edit Profile
                </button>
              </div>

              {/* Upload Area */}
              {!preview ? (
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
                    isDragging
                      ? 'border-medical-500 bg-medical-50 dark:bg-medical-900/20'
                      : 'border-gray-300 dark:border-gray-600 hover:border-medical-500 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                  } cursor-pointer group`}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept={accept}
                    onChange={handleInputChange}
                    className="hidden"
                  />
                  <div className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                    <Upload className="w-10 h-10 text-medical-600 dark:text-medical-400" />
                  </div>
                  <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Upload Clinical Scan</h4>
                  <p className="text-gray-500 dark:text-gray-400 text-sm max-w-xs mx-auto">
                    Drag and drop your {title.toLowerCase()} image here, or click to browse files
                  </p>
                  <div className="mt-6 flex items-center justify-center gap-4 text-xs font-bold text-gray-400 uppercase tracking-widest">
                    <span>PNG</span>
                    <span className="w-1 h-1 bg-gray-300 rounded-full"></span>
                    <span>JPG</span>
                    <span className="w-1 h-1 bg-gray-300 rounded-full"></span>
                    <span>JPEG</span>
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="relative rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-900">
                    <img src={preview} alt="Preview" className="w-full h-72 object-contain" />
                    <button
                      onClick={handleRemoveFile}
                      className="absolute top-4 right-4 p-2 bg-red-500/90 hover:bg-red-600 text-white rounded-full shadow-lg transition-all"
                    >
                      <X className="w-5 h-5" />
                    </button>
                    <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/50 to-transparent">
                      <p className="text-white text-xs font-medium truncate">{file.name}</p>
                    </div>
                  </div>

                  {isPredicting && (
                    <div className="space-y-3">
                      <div className="flex justify-between text-xs font-bold text-medical-600 dark:text-medical-400 uppercase tracking-widest">
                        <span>AI Neural Processing...</span>
                        <span>{progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
                        <div
                          className="bg-medical-600 h-full rounded-full transition-all duration-300 shadow-[0_0_15px_rgba(37,99,235,0.5)]"
                          style={{ width: `${progress}%` }}
                        ></div>
                      </div>
                    </div>
                  )}

                  {!result && (
                    <button
                      onClick={handlePredict}
                      disabled={isPredicting}
                      className="w-full py-4 bg-medical-600 text-white font-bold rounded-xl hover:bg-medical-700 disabled:opacity-50 transition-all flex items-center justify-center gap-3 shadow-lg shadow-medical-600/30"
                    >
                      {isPredicting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Activity className="w-5 h-5" />}
                      {isPredicting ? 'Analyzing Scan...' : 'Start AI Diagnosis'}
                    </button>
                  )}

                  {result && !result.error && (
                    <div className="animate-in zoom-in-95 duration-300">
                      <div className={`p-6 rounded-2xl border-2 ${
                        isDiseaseDetected
                          ? 'bg-red-50/50 border-red-500/30 dark:bg-red-900/10 dark:border-red-500/50'
                          : 'bg-green-50/50 border-green-500/30 dark:bg-green-900/10 dark:border-green-500/50'
                      }`}>
                        <div className="flex items-center justify-between mb-6">
                          <div>
                            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-[0.2em]">Diagnostic Result</span>
                            <h4 className={`text-3xl font-black ${isDiseaseDetected ? 'text-red-600' : 'text-green-600'}`}>
                              {result.prediction}
                            </h4>
                          </div>
                          <div className="text-right">
                            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-[0.2em]">Confidence</span>
                            <h4 className="text-3xl font-black text-gray-900 dark:text-white">
                              {result.confidence}%
                            </h4>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 py-4 border-t border-gray-200 dark:border-gray-700">
                          <div className="flex flex-col">
                            <span className="text-[10px] font-bold text-gray-400 uppercase">Patient</span>
                            <span className="font-bold dark:text-white">{patientDetails.name}</span>
                          </div>
                          <div className="flex flex-col text-right">
                            <span className="text-[10px] font-bold text-gray-400 uppercase">Case Status</span>
                            <span className={`font-bold ${isDiseaseDetected ? 'text-red-500' : 'text-green-500'}`}>
                              {isDiseaseDetected ? 'Action Required' : 'Cleared'}
                            </span>
                          </div>
                        </div>

                        {result.download_url && (
                          <a
                            href={`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}${result.download_url}`}
                            target="_blank"
                            rel="noreferrer"
                            className="mt-4 w-full py-4 bg-gray-900 dark:bg-white dark:text-gray-900 text-white font-bold rounded-xl hover:opacity-90 transition-all flex items-center justify-center gap-3"
                          >
                            <Download className="w-5 h-5" />
                            Download Medical Report
                          </a>
                        )}
                      </div>
                    </div>
                  )}

                  {result && result.error && (
                    <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm font-medium">
                      {result.error}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadCard;
