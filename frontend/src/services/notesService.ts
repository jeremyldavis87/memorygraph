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

export interface Note {
  id: number;
  title: string;
  content?: string;
  original_text?: string;
  summary?: string;
  source_type: string;
  category_id?: number;
  file_path?: string;
  image_path?: string;
  ocr_mode: string;
  ocr_confidence?: number;
  processing_status: string;
  entities?: any[];
  action_items?: any[];
  tags?: any[];
  metadata?: any;
  created_at: string;
  updated_at?: string;
  captured_at?: string;
}

export interface NoteListResponse {
  notes: Note[];
  total: number;
  page: number;
  size: number;
}

export interface NoteCreate {
  title: string;
  content?: string;
  original_text?: string;
  source_type?: string;
  category_id?: number;
  file_path?: string;
  image_path?: string;
  ocr_mode?: string;
}

export const notesService = {
  async getNotes(params?: {
    skip?: number;
    limit?: number;
    category_id?: number;
    search?: string;
  }): Promise<NoteListResponse> {
    const response = await api.get('/notes', { params });
    return response.data;
  },

  async getNote(id: number): Promise<Note> {
    const response = await api.get(`/notes/${id}`);
    return response.data;
  },

  async createNote(note: NoteCreate): Promise<Note> {
    const response = await api.post('/notes', note);
    return response.data;
  },

  async updateNote(id: number, updates: Partial<Note>): Promise<Note> {
    const response = await api.put(`/notes/${id}`, updates);
    return response.data;
  },

  async deleteNote(id: number): Promise<void> {
    await api.delete(`/notes/${id}`);
  },

  async uploadNote(
    file: File,
    categoryId?: number,
    ocrMode: string = 'traditional'
  ): Promise<Note> {
    const formData = new FormData();
    formData.append('file', file);
    if (categoryId) {
      formData.append('category_id', categoryId.toString());
    }
    formData.append('ocr_mode', ocrMode);

    const response = await api.post('/notes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};