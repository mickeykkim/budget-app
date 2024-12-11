import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { BankAccount } from '../types';

interface AccountsPageProps {
  accounts?: BankAccount[];
  isLoading?: boolean;
}

const AccountsPage: React.FC<AccountsPageProps> = ({ 
  accounts = [], 
  isLoading = false 
}) => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Accounts</h1>
      <div className="grid gap-4">
        {isLoading ? (
          <Card>
            <CardContent className="p-6">
              <div className="animate-pulse flex space-x-4">
                <div className="flex-1 space-y-4 py-1">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="space-y-2">
                    <div className="h-4 bg-gray-200 rounded"></div>
                    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : accounts.length === 0 ? (
          <Card>
            <CardContent className="p-6">
              <p className="text-gray-500">No connected bank accounts</p>
            </CardContent>
          </Card>
        ) : (
          accounts.map((account) => (
            <Card key={account.id}>
              <CardContent className="p-6">
                <h2 className="font-semibold">{account.account_name}</h2>
                <p className="text-sm text-gray-500">{account.account_identifier}</p>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default AccountsPage;