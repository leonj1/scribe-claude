import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to attach token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  getGoogleLoginUrl() {
    return `${API_URL}/auth/google/login`;
  }

  // Recording endpoints
  async getRecordings() {
    const response = await this.client.get('/recordings');
    return response.data;
  }

  async getRecording(recordingId: string) {
    const response = await this.client.get(`/recordings/${recordingId}`);
    return response.data;
  }

  async createRecording() {
    const response = await this.client.post('/recordings');
    return response.data;
  }

  async uploadChunk(recordingId: string, chunkIndex: number, audioBlob: Blob) {
    const formData = new FormData();
    formData.append('chunk_index', chunkIndex.toString());
    formData.append('audio_chunk', audioBlob, `chunk_${chunkIndex}.webm`);

    const response = await this.client.post(
      `/recordings/${recordingId}/chunks`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async pauseRecording(recordingId: string) {
    const response = await this.client.patch(`/recordings/${recordingId}/pause`);
    return response.data;
  }

  async finishRecording(recordingId: string) {
    const response = await this.client.post(`/recordings/${recordingId}/finish`);
    return response.data;
  }

  async updateRecordingNotes(recordingId: string, notes: string) {
    const formData = new FormData();
    formData.append('notes', notes);

    const response = await this.client.patch(
      `/recordings/${recordingId}/notes`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }
}

export const apiService = new ApiService();
