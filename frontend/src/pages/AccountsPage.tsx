import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useBankAccounts } from '@/hooks/useBankAccounts';
import { Plus, Trash2 } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { ConfirmDialog } from '@/components/ui/alert-dialog';
import { AlertCircle } from 'lucide-react';
import { AddAccountModal } from '@/components/AddAccountModal';
import type { CreateBankAccountData } from '@/types';

const AccountsPage: React.FC = () => {
  const { accounts, loading, error, removeAccount, createAccount, isCreating } = useBankAccounts();
  const [deleteAccountId, setDeleteAccountId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);

  const handleRemoveAccount = async () => {
    if (!deleteAccountId) return;

    try {
      await removeAccount(deleteAccountId);
      setDeleteAccountId(null);
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : 'Failed to remove account';

      setDeleteError(errorMessage);
      console.error('Failed to remove account', err);
    }
  };

  const handleCreateAccount = async (data: CreateBankAccountData) => {
    try {
      await createAccount(data);
      setIsAddModalOpen(false);
      setAddError(null);
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : 'Failed to create account';
      setAddError(errorMessage);
    }
  };

  const clearErrors = () => {
    setDeleteError(null);
    setAddError(null);
  };

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>Failed to load accounts: {error.message}</AlertDescription>
      </Alert>
    );
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Accounts</h1>
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, index) => (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {(deleteError || addError) && (
        <Alert variant="destructive" className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {deleteError || addError}
            <div className="mt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={clearErrors}
                className="mr-2"
              >
                Dismiss
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}

      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Accounts</h1>
        <Button
          variant="outline"
          className="flex items-center gap-2"
          onClick={() => setIsAddModalOpen(true)}
        >
          <Plus className="h-4 w-4" /> Add Account
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {accounts.length === 0 ? (
          <Card>
            <CardContent className="p-6">
              <p className="text-gray-500">No connected bank accounts</p>
            </CardContent>
          </Card>
        ) : (
          accounts.map((account) => (
            <Card key={account.id}>
              <CardHeader className="flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle>{account.account_name}</CardTitle>
                <Button
                  variant="destructive"
                  size="icon"
                  onClick={() => setDeleteAccountId(account.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground">
                  {account.account_identifier}
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  {account.is_active ? 'Active' : 'Inactive'}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      <AddAccountModal
        isOpen={isAddModalOpen}
        onOpenChange={setIsAddModalOpen}
        onSubmit={handleCreateAccount}
        isLoading={isCreating}
      />

      <ConfirmDialog
        open={deleteAccountId !== null}
        onOpenChange={() => setDeleteAccountId(null)}
        title="Delete Account"
        description="Are you sure you want to delete this account? This action cannot be undone."
        onConfirm={handleRemoveAccount}
      />
    </div>
  );
};

export default AccountsPage;