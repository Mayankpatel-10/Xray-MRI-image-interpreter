import { useState, useRef } from 'react';
import { Upload, X, Image as ImageIcon, Loader2 } from 'lucide-react';

const UploadCard = ({ title, description, icon: Icon, accept, onPredict, apiEndpoint }) => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);
  const [result, setResult] = useState(null);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef(null);

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile) return;

    // Validate file type
    const validTypes = accept.split(',').map(type => type.trim());
    const fileExtension = `.${selectedFile.name.split('.').pop().toLowerCase()}`;
    
    if (!validTypes.includes(fileExtension) && !validTypes.includes(selectedFile.type)) {
      alert(`Please upload a valid ${title.toLowerCase()} image file`);
      return;
    }

    // Validate file size (max 10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB');
      return;
    }

    setFile(selectedFile);
    setResult(null);
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target.result);
    };
    reader.readAsDataURL(selectedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFileSelect(droppedFile);
  };

  const handleInputChange = (e) => {
    const selectedFile = e.target.files[0];
    handleFileSelect(selectedFile);
  };

  const handleRemoveFile = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handlePredict = async () => {
    if (!file) return;

    setIsPredicting(true);
    setProgress(0);

    // Simulate progress
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
      const response = await onPredict(file);
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

  const isDiseaseDetected = result && result.prediction && 
    (result.prediction.toLowerCase().includes('tumor') || 
     result.prediction.toLowerCase().includes('pneumonia') ||
     result.prediction.toLowerCase().includes('positive'));

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-shadow duration-300">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 rounded-xl bg-medical-100 dark:bg-medical-900/50">
            <Icon className="w-6 h-6 text-medical-600 dark:text-medical-400" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">{title}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
          </div>
        </div>

        {/* Upload Area */}
        {!preview ? (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
              isDragging
                ? 'border-medical-500 bg-medical-50 dark:bg-medical-900/20'
                : 'border-gray-300 dark:border-gray-600 hover:border-medical-500 hover:bg-gray-50 dark:hover:bg-gray-700/50'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept={accept}
              onChange={handleInputChange}
              className="hidden"
            />
            <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="text-gray-700 dark:text-gray-300 font-medium mb-2">
              Drop your image here, or click to browse
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Supports: {accept}
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
              Maximum file size: 10MB
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Preview */}
            <div className="relative group">
              <img
                src={preview}
                alt="Preview"
                className="w-full h-64 object-contain rounded-xl bg-gray-100 dark:bg-gray-700"
              />
              <button
                onClick={handleRemoveFile}
                className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* File Info */}
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <ImageIcon className="w-4 h-4" />
                <span className="truncate max-w-[200px]">{file.name}</span>
              </div>
              <span className="text-gray-500 dark:text-gray-500">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </span>
            </div>

            {/* Progress Bar */}
            {isPredicting && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                  <span>Analyzing image...</span>
                  <span>{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-medical-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Predict Button */}
            <button
              onClick={handlePredict}
              disabled={isPredicting}
              className="w-full py-3 px-6 bg-medical-600 text-white font-semibold rounded-lg hover:bg-medical-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isPredicting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                'Predict'
              )}
            </button>

            {/* Result */}
            {result && !result.error && (
              <div
                className={`p-4 rounded-xl border-2 ${
                  isDiseaseDetected
                    ? 'bg-red-50 border-red-500 dark:bg-red-900/20 dark:border-red-400'
                    : 'bg-green-50 border-green-500 dark:bg-green-900/20 dark:border-green-400'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                      Prediction Result
                    </p>
                    <p
                      className={`text-2xl font-bold ${
                        isDiseaseDetected
                          ? 'text-red-700 dark:text-red-400'
                          : 'text-green-700 dark:text-green-400'
                      }`}
                    >
                      {result.prediction}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                      Confidence
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {result.confidence}%
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Error */}
            {result && result.error && (
              <div className="p-4 rounded-xl bg-red-50 border-2 border-red-500 dark:bg-red-900/20 dark:border-red-400">
                <p className="text-red-700 dark:text-red-400 font-medium">{result.error}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadCard;
