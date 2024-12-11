import * as React from 'react';
import { renderHook, waitFor } from '@testing-library/react';
import { useUser, useBankAccounts, useLoginMutation } from '../useQueries';
import { mockUser, mockBankAccount } from '../../test/utils';
import { vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthContext';
import { BrowserRouter } from 'react-router-dom';
import { api } from '../../lib/api/client';
import type { ApiResponse } from '../../lib/api/types';
import type { AuthResponse, PaginatedResponse } from '../../types';

// Create a new QueryClient instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

// Define wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>{children}</AuthProvider>
      </QueryClientProvider>
    </BrowserRouter>
  );
};

describe('API Hooks', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    queryClient.clear();
  });

  describe('useUser', () => {
    it('fetches user data successfully', async () => {
      const mockResponse = {
        data: mockUser,
        status: 200,
        headers: {},
      } satisfies ApiResponse<typeof mockUser>;
      
      vi.spyOn(api, 'getUser').mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useUser(), {
        wrapper: TestWrapper
      });

      expect(result.current.isLoading).toBe(true);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockUser);
    });

    it('handles user fetch error', async () => {
      const error = new Error('Failed to fetch user');
      vi.spyOn(api, 'getUser').mockRejectedValue(error);

      const { result } = renderHook(() => useUser(), {
        wrapper: TestWrapper
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeDefined();
    });
  });

  describe('useBankAccounts', () => {
    const mockAccounts = {
      items: [mockBankAccount],
      total: 1,
    } satisfies PaginatedResponse<typeof mockBankAccount>;

    it('fetches bank accounts successfully', async () => {
      const mockResponse = {
        data: mockAccounts,
        status: 200,
        headers: {},
      } satisfies ApiResponse<typeof mockAccounts>;
      
      vi.spyOn(api, 'getBankAccounts').mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useBankAccounts(), {
        wrapper: TestWrapper
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockAccounts);
    });
  });

  describe('useLoginMutation', () => {
    it('handles login mutation successfully', async () => {
      const mockAuthResponse = {
        access_token: 'fake-token',
        token_type: 'bearer',
      } satisfies AuthResponse;

      const mockResponse = {
        data: mockAuthResponse,
        status: 200,
        headers: {},
      } satisfies ApiResponse<AuthResponse>;
      
      vi.spyOn(api, 'login').mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useLoginMutation(), {
        wrapper: TestWrapper
      });

      result.current.mutate({ 
        email: 'test@example.com', 
        password: 'password123',
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockAuthResponse);
    });

    it('handles login error', async () => {
      const error = new Error('Invalid credentials');
      vi.spyOn(api, 'login').mockRejectedValue(error);

      const { result } = renderHook(() => useLoginMutation(), {
        wrapper: TestWrapper
      });

      result.current.mutate({ 
        email: 'test@example.com', 
        password: 'wrong-password',
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeDefined();
    });
  });
});