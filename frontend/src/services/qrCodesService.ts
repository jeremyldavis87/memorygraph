import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api/v1';

export interface QRCodeMapping {
  qr_code: string;
  category_id: number;
  category_name: string;
  created_at: string;
  updated_at: string;
}

export interface QRCodeDetection {
  qr_code: string;
  mapped: boolean;
  category_id?: number;
  category_name?: string;
}

class QRCodesService {
  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  async getMappings(): Promise<QRCodeMapping[]> {
    const response = await axios.get(`${API_URL}/qr-codes/`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async mapQRCode(qrCode: string, categoryId: number): Promise<any> {
    const response = await axios.post(`${API_URL}/qr-codes/map`, {
      qr_code: qrCode,
      category_id: categoryId,
    }, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async detectQRCode(qrCode: string): Promise<QRCodeDetection> {
    const response = await axios.get(`${API_URL}/qr-codes/detect/${encodeURIComponent(qrCode)}`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async removeMapping(qrCode: string): Promise<any> {
    const response = await axios.delete(`${API_URL}/qr-codes/${encodeURIComponent(qrCode)}`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async getUnmappedQRCodes(): Promise<any[]> {
    const response = await axios.get(`${API_URL}/qr-codes/unmapped`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }
}

export const qrCodesService = new QRCodesService();
