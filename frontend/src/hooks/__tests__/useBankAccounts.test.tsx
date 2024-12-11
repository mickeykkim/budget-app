// src/hooks/__tests__/useBankAccounts.test.tsx
import { renderHook, act } from '@testing-library/react';
import { waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { useBankAccounts } from '../useBankAccounts';
import { mockBankAccount } from '@/test/utils';
import { server } from '@/test/mocks/server';
import { http, HttpResponse } from 'msw';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
    logger: {
      log: console.log,
      warn: console.warn,
      error: () => {},
    }
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useBankAccounts', () => {
  beforeEach(() => {
    server.resetHandlers();
  });

  it('should fetch bank accounts', async () => {
    // Mock successful response
    server.use(
      http.get('http://localhost:8000/api/v1/bank-accounts', () => {
        return HttpResponse.json({
          items: [mockBankAccount],
          total: 1
        });
      })
    );

    const { result } = renderHook(() => useBankAccounts(), {
      wrapper: createWrapper()
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.accounts).toEqual([mockBankAccount]);
  });

  it('should handle adding a bank account', async () => {
    const newAccount = {
      account_name: 'New Account',
      account_type: 'checking',
      account_identifier: '1234'
    };

    server.use(
      http.post('http://localhost:8000/api/v1/bank-accounts', async () => {
        return HttpResponse.json({
          ...newAccount,
          id: 'new-id',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          is_active: true
        }, { status: 201 });
      })
    );

    const { result } = renderHook(() => useBankAccounts(), {
      wrapper: createWrapper()
    });

    await act(async () => {
      await result.current.addAccount(newAccount);
    });

    await waitFor(() => {
      expect(result.current.isAddingAccount).toBe(false);
    });
  });

  it('should handle updating a bank account', async () => {
    const updateData = {
      id: mockBankAccount.id,
      account_name: 'Updated Account'
    };

    server.use(
      http.patch(`http://localhost:8000/api/v1/bank-accounts/${updateData.id}`, async () => {
        return HttpResponse.json({
          ...mockBankAccount,
          ...updateData,
          updated_at: '2024-01-01T00:00:00Z'
        });
      })
    );

    const { result } = renderHook(() => useBankAccounts(), {
      wrapper: createWrapper()
    });

    await act(async () => {
      await result.current.updateAccount(updateData);
    });

    await waitFor(() => {
      expect(result.current.isUpdatingAccount).toBe(false);
    });
  });

  it('should handle deleting a bank account', async () => {
    server.use(
      http.delete(`http://localhost:8000/api/v1/bank-accounts/${mockBankAccount.id}`, () => {
        return new HttpResponse(null, { status: 204 });
      })
    );

    const { result } = renderHook(() => useBankAccounts(), {
      wrapper: createWrapper()
    });

    await act(async () => {
      await result.current.removeAccount(mockBankAccount.id);
    });

    await waitFor(() => {
      expect(result.current.isRemovingAccount).toBe(false);
    });
  });

  it('should handle errors', async () => {
    server.use(
      http.get('http://localhost:8000/api/v1/bank-accounts', () => {
        return HttpResponse.json(
          { detail: 'Failed to fetch accounts' },
          { status: 500 }
        );
      })
    );

    const { result } = renderHook(() => useBankAccounts(), {
      wrapper: createWrapper()
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
      expect(result.current.error).toBeDefined();
    });
  });
});
