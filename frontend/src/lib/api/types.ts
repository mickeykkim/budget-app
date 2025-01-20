// src/lib/api/types.ts
export interface ApiConfig {
    baseURL: string;
    headers?: Record<string, string>;
    timeout?: number;
  }
  
  export interface ApiResponse<T> {
    data: T;
    status: number;
    headers: Record<string, string>;
  }
  
  export interface ApiError {
    message: string;
    status?: number;
    code?: string;
  }