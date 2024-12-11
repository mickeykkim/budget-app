import axios, { AxiosInstance, AxiosError } from 'axios';
import { ApiConfig, ApiResponse, ApiError } from './types';
import { AuthResponse, User, BankAccount, PaginatedResponse } from '../../types';

class ApiClient {
  private client: AxiosInstance;
  
  constructor(config: ApiConfig) {
    this.client = axios.create({
      baseURL: config.baseURL,
      headers: config.headers,
      timeout: config.timeout || 10000,
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => this.handleError(error)
    );
  }

  private handleError(error: AxiosError): never {
    const apiError: ApiError = {
      message: error.message,
      status: error.response?.status,
      code: error.code,
    };

    // Handle specific error cases
    if (error.response?.status === 401) {
      // Clear auth state and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }

    throw apiError;
  }

  // Add auth token to requests
  setAuthToken(token: string) {
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<ApiResponse<AuthResponse>> {
    const response = await this.client.post<AuthResponse>('/api/v1/auth/login', 
      new URLSearchParams({
        username: email,
        password: password,
      }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    
    return {
      data: response.data,
      status: response.status,
      headers: response.headers as Record<string, string>,
    };
  }

  async getUser(): Promise<ApiResponse<User>> {
    const response = await this.client.get<User>('/api/v1/auth/me');
    return {
      data: response.data,
      status: response.status,
      headers: response.headers as Record<string, string>,
    };
  }

  // Bank accounts endpoints
  async getBankAccounts(): Promise<ApiResponse<PaginatedResponse<BankAccount>>> {
    const response = await this.client.get<PaginatedResponse<BankAccount>>('/api/v1/bank-accounts');
    return {
      data: response.data,
      status: response.status,
      headers: response.headers as Record<string, string>,
    };
  }
}

// Create and export default instance
export const api = new ApiClient({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
});

export default ApiClient;