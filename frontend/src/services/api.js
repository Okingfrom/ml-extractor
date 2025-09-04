import axios from 'axios';
import { logger } from '../utils/logger';

// Create axios instance with default config
// Uses environment variables for API base URL
const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log request in development
    logger.request(config.method, config.url);
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    // Log response in development
    logger.response(response.config.method, response.config.url, response.status);
    
    return response;
  },
  (error) => {
    // Log error in development
    logger.requestError(error.config?.method, error.config?.url, error.response?.status);
    
    // Handle common errors
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    
    // Handle network errors
    if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || !error.response) {
      logger.error('Network error - Backend server may be down');
      error.message = 'Error de conexión con el servidor. Verifica que el backend esté ejecutándose.';
    }
    
    return Promise.reject(error);
  }
);

export default api;
