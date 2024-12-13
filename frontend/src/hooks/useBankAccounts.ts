import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { BankAccount, PaginatedResponse, CreateBankAccountData } from '@/types';

export function useBankAccounts() {
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        const response = await api.get<PaginatedResponse<BankAccount>>('/bank-accounts');
        setAccounts(response.items);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch accounts'));
        setLoading(false);
      }
    };

    fetchAccounts();
  }, []);

  const createAccount = async (data: CreateBankAccountData) => {
    setIsCreating(true);
    try {
      const response = await api.post<BankAccount>('/bank-accounts', data);
      setAccounts(prev => [...prev, response]);
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : 'Failed to create account';
      setError(new Error(errorMessage));
      throw err;
    } finally {
      setIsCreating(false);
    }
  };

  const removeAccount = async (accountId: string) => {
    try {
      await api.delete(`/bank-accounts/${accountId}`);
      setAccounts(prev => prev.filter(account => account.id !== accountId));
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : 'Failed to remove account';
      setError(new Error(errorMessage));
      throw err;
    }
  };

  return {
    accounts,
    loading,
    error,
    isCreating,
    createAccount,
    removeAccount
  };
}