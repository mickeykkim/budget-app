// src/hooks/useTransactions.ts
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { Transaction, TransactionList } from '@/types';

interface TransactionFilters {
  bankAccountId?: string;
  startDate?: Date | null;
  endDate?: Date | null;
  skip?: number;
  limit?: number;
}

export function useTransactions(filters: TransactionFilters = {}) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const params = new URLSearchParams();
        if (filters.bankAccountId) params.append('bank_account_id', filters.bankAccountId);
        if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
        if (filters.limit !== undefined) params.append('limit', filters.limit.toString());
        if (filters.startDate) params.append('start_date', filters.startDate.toISOString());
        if (filters.endDate) params.append('end_date', filters.endDate.toISOString());

        const response = await api.get<TransactionList>(`/transactions${params.toString() ? `?${params.toString()}` : ''}`);

        setTransactions(response.items);
        setTotal(response.total);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch transactions'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchTransactions();
  }, [JSON.stringify(filters)]);

  return {
    transactions,
    total,
    isLoading,
    error
  };
}