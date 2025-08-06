/**
 * API Service for Instagram Analytics
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const analyticsAPI = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Profiles
  getProfiles: () => api.get('/profiles'),
  getProfile: (username) => api.get(`/profiles/${username}`),

  // Media
  getMedia: (params = {}) => api.get('/media', { params }),
  getStories: (params = {}) => api.get('/stories', { params }),

  // Analytics
  getInsights: (params = {}) => api.get('/analytics/insights', { params }),
  getWeeklyComparison: (params = {}) => api.get('/analytics/weekly-comparison', { params }),
  getDailyMetrics: (params = {}) => api.get('/analytics/daily-metrics', { params }),

  // Data management
  fetchData: (username = null) => api.post('/fetch-data', username ? { username } : {}),
  exportCSV: (params = {}) => api.get('/export/csv', { params }),

  // Summary
  getSummaryStats: () => api.get('/stats/summary'),
};

export default analyticsAPI;
