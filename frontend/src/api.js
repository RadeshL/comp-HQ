import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Component API endpoints
export const componentAPI = {
  // Submit list of components
  submitComponents: async (components) => {
    const response = await api.post('/api/components/', { components });
    return response.data;
  },

  // Get ranked products for a component
  getRankedProducts: async (componentName, sessionId) => {
    const response = await api.get(`/api/components/products/${componentName}`, {
      params: { session_id: sessionId }
    });
    return response.data;
  },

  // Select a product
  selectProduct: async (componentName, productId, sessionId) => {
    const response = await api.post('/api/components/select', {
      component_name: componentName,
      product_id: productId,
      session_id: sessionId
    });
    return response.data;
  },

  // Get all selections for a session
  getSessionSelections: async (sessionId) => {
    const response = await api.get(`/api/components/selections/${sessionId}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/api/components/health');
    return response.data;
  }
};

// Report API endpoints
export const reportAPI = {
  // Generate procurement report
  generateReport: async (sessionId) => {
    const response = await api.post('/api/reports/generate', { session_id: sessionId });
    return response.data;
  },

  // Download report
  downloadReport: async (filename) => {
    const response = await api.get(`/api/reports/download/${filename}`, {
      responseType: 'blob'
    });
    return response;
  },

  // List all reports
  listReports: async () => {
    const response = await api.get('/api/reports/list');
    return response.data;
  },

  // Delete report
  deleteReport: async (filename) => {
    const response = await api.delete(`/api/reports/${filename}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/api/reports/health');
    return response.data;
  }
};

// General API endpoints
export const generalAPI = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },

  // API info
  getInfo: async () => {
    const response = await api.get('/api/info');
    return response.data;
  }
};

export default api;
