// src/types/index.ts

// Auth types
export interface User {
    id: string;
    email: string;
    created_at: string;
    updated_at: string;
  }
  
  export interface AuthResponse {
    access_token: string;
    token_type: string;
  }
  
  export interface LoginCredentials {
    email: string;
    password: string;
  }
  
  // Bank Account types
  export interface BankAccount {
    id: string;
    account_type: string;
    account_name: string;
    account_identifier: string;
    created_at: string;
    is_active: boolean;
  }
  
  export interface PaginatedResponse<T> {
    items: T[];
    total: number;
  }
  
  // API Error type
  export interface ApiError {
    detail: string;
    status?: number;
  }
  
  // Route types
  export interface ProtectedRouteProps {
    children: React.ReactNode;
  }
  
  // Component prop types
  export interface LayoutProps {
    children?: React.ReactNode;
  }