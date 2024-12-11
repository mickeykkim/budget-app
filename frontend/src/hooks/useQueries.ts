// src/hooks/useQueries.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api/client";

export function useUser() {
  return useQuery({
    queryKey: ['user'],
    queryFn: async () => {
      const response = await api.getUser();
      return response.data;
    },
  });
}

export function useBankAccounts() {
  return useQuery({
    queryKey: ['bankAccounts'],
    queryFn: async () => {
      const response = await api.getBankAccounts();
      return response.data;
    },
  });
}

export function useLoginMutation() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      const response = await api.login(email, password);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
  });
}