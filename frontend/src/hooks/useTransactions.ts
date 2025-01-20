// src/hooks/useTransactions.ts
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type {
  Transaction,
  CreateTransactionData,
  UpdateTransactionData,
  TransactionQueryParams,
  PaginatedResponse
} from '@/types';

export function useTransactions(filters: TransactionQueryParams = {}) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setIsLoading(true);
        const response = await api.get<PaginatedResponse<Transaction>>('/transactions', { params: filters });
        setTransactions(response.items);
        setTotal(response.total);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch transactions'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchTransactions();
  }, [JSON.stringify(filters)]);

  const createTransaction = async (data: CreateTransactionData) => {
    setIsCreating(true);
    try {
      const responseData = await api.post<Transaction>('/transactions', data);
      setTransactions(prev => [...prev, responseData]);
      setTotal(prev => prev + 1);
      return responseData;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to create transaction');
    } finally {
      setIsCreating(false);
    }
  };

  const updateTransaction = async (id: string, data: UpdateTransactionData) => {
    setIsUpdating(true);
    try {
      const responseData = await api.patch<Transaction>(`/transactions/${id}`, data);
      setTransactions(prev =>
        prev.map(t => (t.id === id ? responseData : t))
      );
      setError(null);
      return responseData;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to update transaction'));
      throw err;
    } finally {
      setIsUpdating(false);
    }
  };

  const deleteTransaction = async (id: string) => {
    setIsDeleting(true);
    try {
      await api.delete(`/transactions/${id}`);
      setTransactions(prev => prev.filter(t => t.id !== id));
      setTotal(prev => prev - 1);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to delete transaction'));
      throw err;
    } finally {
      setIsDeleting(false);
    }
  };

  return {
    transactions,
    total,
    isLoading,
    isCreating,
    isUpdating,
    isDeleting,
    error,
    createTransaction,
    updateTransaction,
    deleteTransaction
  };
}