import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

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

export interface SearchSuggestion {
  text: string;
  type: string;
}

export const searchService = {
  async search(query: string, type: 'notes' | 'entities' = 'notes') {
    const endpoint = type === 'notes' ? '/search/notes' : '/search/entities';
    const response = await api.get(endpoint, {
      params: { q: query }
    });
    return response.data;
  },

  async getSuggestions(query: string) {
    const response = await api.get('/search/suggestions', {
      params: { q: query }
    });
    return response.data;
  },
};