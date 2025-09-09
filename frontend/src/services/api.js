import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized access
      console.error('Unauthorized access');
    } else if (error.response?.status >= 500) {
      // Handle server errors
      console.error('Server error:', error.response.data);
    }
    
    return Promise.reject(error);
  }
);

// Advisor verification API
export const advisorAPI = {
  verify: (data) => api.post('/advisors/verify', data),
  search: (params) => api.get('/advisors/search', { params }),
  getStats: () => api.get('/advisors/stats'),
  getDetails: (sebiNumber) => api.get(`/advisors/${sebiNumber}`),
  list: (params) => api.get('/advisors', { params }),
  reportSuspicious: (data) => api.post('/advisors/report-suspicious', data),
};

// Content scanner API
export const scannerAPI = {
  analyze: (data) => api.post('/scanner/analyze-text', data),
  analyzeUrl: (data) => api.post('/scanner/analyze-url', data),
  batchAnalyze: (data) => api.post('/scanner/batch-analyze', data),
  getFraudKeywords: () => api.get('/scanner/fraud-keywords'),
  testDetection: () => api.post('/scanner/test-detection'),
  getDetectionStats: () => api.get('/scanner/detection-stats'),
};

// Dashboard API
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getFlaggedContent: (params) => api.get('/dashboard/flagged-content', { params }),
  getTrends: (params) => api.get('/dashboard/trends', { params }),
  getAlerts: (params) => api.get('/dashboard/alerts', { params }),
  exportData: (params) => api.get('/dashboard/export', { params }),
  getFraudTypesChart: (params) => api.get('/dashboard/charts/fraud-types', { params }),
  getRiskDistributionChart: () => api.get('/dashboard/charts/risk-distribution'),
  getSummaryMetrics: () => api.get('/dashboard/summary'),
};

// Utility functions
export const formatError = (error) => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  } else if (error.response?.data?.message) {
    return error.response.data.message;
  } else if (error.message) {
    return error.message;
  } else {
    return 'An unexpected error occurred';
  }
};

export const formatRiskScore = (score) => {
  if (score >= 80) return { level: 'critical', color: '#dc2626', text: 'Critical Risk' };
  if (score >= 60) return { level: 'high', color: '#ef4444', text: 'High Risk' };
  if (score >= 40) return { level: 'medium', color: '#f59e0b', text: 'Medium Risk' };
  if (score >= 20) return { level: 'low', color: '#10b981', text: 'Low Risk' };
  return { level: 'minimal', color: '#6b7280', text: 'Minimal Risk' };
};

export const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatDateTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const downloadFile = (data, filename, type = 'application/json') => {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand('copy');
      document.body.removeChild(textArea);
      return true;
    } catch (err) {
      document.body.removeChild(textArea);
      return false;
    }
  }
};

export const validateSebiNumber = (sebiNumber) => {
  // SEBI registration number format: INA followed by 9 digits
  const sebiPattern = /^INA\d{9}$/;
  return sebiPattern.test(sebiNumber);
};

export const validateEmail = (email) => {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailPattern.test(email);
};

export const validatePhoneNumber = (phone) => {
  // Indian phone number validation
  const phonePattern = /^[6-9]\d{9}$/;
  return phonePattern.test(phone.replace(/\D/g, ''));
};

export const sanitizeInput = (input) => {
  return input
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .trim()
    .substring(0, 1000); // Limit length
};

export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const throttle = (func, limit) => {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

export const getTimeAgo = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);

  if (diffInSeconds < 60) {
    return 'Just now';
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  } else if (diffInSeconds < 2592000) {
    const days = Math.floor(diffInSeconds / 86400);
    return `${days} day${days > 1 ? 's' : ''} ago`;
  } else {
    return date.toLocaleDateString('en-IN');
  }
};

export default api;
