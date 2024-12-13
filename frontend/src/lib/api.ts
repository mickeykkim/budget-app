import axios, { AxiosError } from 'axios';

class ApiClient {
  private client;

  constructor() {
    this.client = axios.create({
      baseURL: '/api/v1',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      }
    });

    this.client.interceptors.request.use(config => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      response => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async login(email: string, password: string) {
    try {
      // Login endpoint specifically needs form data
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await this.client.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async get<T>(url: string, config = {}) {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data = {}, config = {}) {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data = {}, config = {}) {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async patch<T>(url: string, data = {}, config = {}) {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  async delete(url: string, config = {}) {
    const response = await this.client.delete(url, config);
    return response.data;
  }
}

export const api = new ApiClient();