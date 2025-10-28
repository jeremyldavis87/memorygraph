import axios from 'axios';
import { logger } from '../utils/logger';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  logger.debug('API Request', {
    method: config.method?.toUpperCase(),
    url: config.url,
    baseURL: config.baseURL,
    hasToken: !!token,
  });
  
  return config;
}, (error) => {
  logger.error('Request Error', error);
  return Promise.reject(error);
});

// Handle token expiration
api.interceptors.response.use(
  (response) => {
    logger.debug('API Response', {
      status: response.status,
      url: response.config.url,
    });
    return response;
  },
  (error) => {
    logger.error('API Response Error', error, {
      status: error.response?.status,
      url: error.config?.url,
      message: error.message,
    });
    
    if (error.response?.status === 401) {
      // Token expired or invalid
      logger.warn('Authentication failed, redirecting to login');
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  async login(email: string, password: string) {
    logger.info('Login attempt', { email });
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    try {
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      logger.info('Login successful', { email });
      return response.data;
    } catch (error: any) {
      logger.error('Login failed', error, { email });
      throw error;
    }
  },

  async register(email: string, password: string, username: string, fullName?: string) {
    logger.info('Registration attempt', { email, username });
    try {
      const response = await api.post('/auth/register', {
        email,
        password,
        username,
        full_name: fullName,
      });
      logger.info('Registration successful', { email, username });
      return response.data;
    } catch (error: any) {
      logger.error('Registration failed', error, { email, username });
      throw error;
    }
  },

  async getCurrentUser() {
    logger.debug('Getting current user');
    try {
      const response = await api.get('/auth/me');
      logger.debug('Current user retrieved', { user: response.data });
      return response.data;
    } catch (error: any) {
      logger.error('Failed to get current user', error);
      throw error;
    }
  },

  async updateSettings(settings: {
    vision_model_preference?: string;
    ocr_confidence_threshold?: number;
    multi_note_detection_enabled?: boolean;
    default_ocr_mode?: string;
    auto_capture?: boolean;
    ai_processing_enabled?: boolean;
  }) {
    logger.info('Updating user settings', { settings });
    try {
      const response = await api.put('/auth/me/settings', settings);
      logger.info('Settings updated successfully');
      return response.data;
    } catch (error: any) {
      logger.error('Failed to update settings', error, { settings });
      throw error;
    }
  },
};