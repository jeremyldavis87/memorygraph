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

export interface Category {
  id: number;
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  qr_code?: string;
  default_tags?: any[];
  processing_rules?: any;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CategoryCreate {
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  qr_code?: string;
  default_tags?: any[];
  processing_rules?: any;
}

export const categoriesService = {
  async getCategories(): Promise<Category[]> {
    const response = await api.get('/categories');
    return response.data;
  },

  async getCategory(id: number): Promise<Category> {
    const response = await api.get(`/categories/${id}`);
    return response.data;
  },

  async createCategory(category: CategoryCreate): Promise<Category> {
    const response = await api.post('/categories', category);
    return response.data;
  },

  async updateCategory(id: number, updates: Partial<Category>): Promise<Category> {
    const response = await api.put(`/categories/${id}`, updates);
    return response.data;
  },

  async deleteCategory(id: number): Promise<void> {
    await api.delete(`/categories/${id}`);
  },
};