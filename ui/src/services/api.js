import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  timeout: 30000,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

// Request interceptor to add auth token if needed
api.interceptors.request.use(
  (config) => {
    // Add authentication headers for protected routes
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
      
      // Handle 401 Unauthorized - redirect to login
      if (error.response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject({
          message: 'Please login to access this feature',
          status: 401,
        });
      }
      
      return Promise.reject({
        message: error.response.data.message || 'Server error',
        status: error.response.status,
      });
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
      return Promise.reject({
        message: 'Network error. Please check your connection.',
        status: null,
      });
    } else {
      // Error in request setup
      console.error('Request Error:', error.message);
      return Promise.reject({
        message: error.message || 'Request failed',
        status: null,
      });
    }
  }
);

// API functions for medical image prediction
export const predictBrainTumor = async (data) => {
  // If data is already FormData (from new UI), use it directly
  // Otherwise create it (for backward compatibility if needed)
  const formData = data instanceof FormData ? data : new FormData();
  if (!(data instanceof FormData)) {
    formData.append('file', data);
    formData.append('generate_pdf', 'true');
  }
  
  try {
    const response = await api.post('/predict/brain', formData);
    return response.data;
  } catch (error) {
    console.error('Brain tumor prediction error:', error);
    throw error;
  }
};

export const predictPneumonia = async (data) => {
  const formData = data instanceof FormData ? data : new FormData();
  if (!(data instanceof FormData)) {
    formData.append('file', data);
    formData.append('generate_pdf', 'true');
  }
  
  try {
    const response = await api.post('/predict/chest', formData);
    return response.data;
  } catch (error) {
    console.error('Pneumonia prediction error:', error);
    throw error;
  }
};

// Health check to verify backend connection
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default api;
