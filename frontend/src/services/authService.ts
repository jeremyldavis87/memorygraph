import axios from 'axios';

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
  return config;
});

export const authService = {
  async login(email: string, password: string) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  async register(email: string, password: string, username: string, fullName?: string) {
    const response = await api.post('/auth/register', {
      email,
      password,
      username,
      full_name: fullName,
    });
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  async updateSettings(settings: {
    vision_model_preference?: string;
    ocr_confidence_threshold?: number;
    multi_note_detection_enabled?: boolean;
    default_ocr_mode?: string;
    auto_capture?: boolean;
    ai_processing_enabled?: boolean;
  }) {
    const response = await api.put('/auth/me/settings', settings);
    return response.data;
  },
};