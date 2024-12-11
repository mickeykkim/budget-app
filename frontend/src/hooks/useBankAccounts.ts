// src/hooks/useBankAccounts.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import type { BankAccount } from '@/types';

export function useBankAccounts() {
  const queryClient = useQueryClient();

  const accountsQuery = useQuery({
    queryKey: ['bankAccounts'],
    queryFn: async () => {
      const response = await api.getBankAccounts();
      return response.data;
    },
  });

  const addAccountMutation = useMutation({
    mutationFn: async (accountData: Partial<BankAccount>) => {
      const response = await api.createBankAccount(accountData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bankAccounts'] });
    },
  });

  const removeAccountMutation = useMutation({
    mutationFn: async (accountId: string) => {
      await api.deleteBankAccount(accountId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bankAccounts'] });
    },
  });

  const updateAccountMutation = useMutation({
    mutationFn: async ({ id, ...data }: Partial<BankAccount> & { id: string }) => {
      const response = await api.updateBankAccount(id, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bankAccounts'] });
    },
  });

  return {
    accounts: accountsQuery.data?.items ?? [],
    isLoading: accountsQuery.isLoading,
    isError: accountsQuery.isError,
    error: accountsQuery.error,
    addAccount: addAccountMutation.mutate,
    removeAccount: removeAccountMutation.mutate,
    updateAccount: updateAccountMutation.mutate,
    isAddingAccount: addAccountMutation.isPending,
    isRemovingAccount: removeAccountMutation.isPending,
    isUpdatingAccount: updateAccountMutation.isPending,
  };
}