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
  user_id: string;
  account_type: string;
  account_name?: string;
  account_identifier?: string;
  created_at: string;
  is_active: boolean;
}

export interface CreateBankAccountData {
  account_type: string;
  account_name?: string;
  account_identifier?: string;
  access_token: string;
  refresh_token?: string;
  token_expires_at?: string;
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

// Transaction types
export interface Transaction {
  id: string;
  user_id: string;
  bank_account_id: string;
  amount: number;
  description?: string | null;
  created_at: string;
}

export interface CreateTransactionData {
  bank_account_id: string;
  amount: number;
  description?: string;
}

export interface UpdateTransactionData {
  amount: number;
  description?: string;
}

export interface TransactionList {
  items: Transaction[];
  total: number;
}

export interface TransactionQueryParams {
  bank_account_id?: string;
  startDate?: Date;
  endDate?: Date;
  limit?: number;
  skip?: number;
}
