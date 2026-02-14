/**
 * API Service
 * Handles all HTTP requests to backend
 */
import axios from 'axios';

// Base URL for API - change for production
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add JWT token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/**
 * Authentication API
 */
export const authAPI = {
  /**
   * Register new user
   */
  register: async (email, password) => {
    const response = await api.post('/auth/register', { email, password });
    return response.data;
  },

  /**
   * Login user and store token
   */
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    const { access_token } = response.data;
    
    // Store token in localStorage
    localStorage.setItem('access_token', access_token);
    
    return response.data;
  },

  /**
   * Logout user
   */
  logout: () => {
    localStorage.removeItem('access_token');
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Get current user info
   */
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

/**
 * Analysis API
 */
export const analysisAPI = {
  /**
   * Analyze an asset
   */
  analyzeAsset: async (assetName) => {
    const response = await api.post('/analysis/analyze', {
      asset_name: assetName,
    });
    return response.data;
  },

  /**
   * Get user's analysis reports
   */
  getReports: async () => {
    const response = await api.get('/analysis/reports');
    return response.data;
  },

  /**
   * Generate and download PDF for a report
   */
  generatePDF: async (reportId) => {
    const response = await api.post(`/analysis/generate-pdf/${reportId}`, {}, {
      responseType: 'blob'
    });
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `stratify_report_${reportId}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    return { success: true };
  },
};

export default api;
