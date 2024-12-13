import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectItem,
} from '@/components/ui/select';
import { useTransactions } from '@/hooks/useTransactions';
import { useBankAccounts } from '@/hooks/useBankAccounts';
import { formatCurrency, formatDate } from '@/utils/formatting';
import { Filter, Plus } from 'lucide-react';
import { AddTransactionModal } from '@/components/AddTransactionModal';
import { EditTransactionModal } from '@/components/EditTransactionModal';
import { ConfirmDialog } from '@/components/ui/alert-dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CreateTransactionData, Transaction, UpdateTransactionData } from '@/types';

const TransactionsPage: React.FC = () => {
  const { accounts } = useBankAccounts();
  const [selectedAccountId, setSelectedAccountId] = useState<string | undefined>(undefined);
  const [dateRange, setDateRange] = useState<{
    startDate?: Date;
    endDate?: Date
  }>({});
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    transactions,
    total,
    isLoading,
    error: fetchError,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    isCreating,
    isUpdating,
    isDeleting,
  } = useTransactions({
    bankAccountId: selectedAccountId,
    startDate: dateRange.startDate,
    endDate: dateRange.endDate,
    limit: 50,
  });

  const handleCreateTransaction = async (data: CreateTransactionData) => {
    try {
      await createTransaction(data);
      setIsAddModalOpen(false);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : 'Failed to create transaction';
      setError(errorMessage);
    }
  };

  const handleUpdateTransaction = async (data: UpdateTransactionData) => {
    if (!selectedTransaction) return;

    try {
      await updateTransaction(selectedTransaction.id, data);
      setIsEditModalOpen(false);
      setSelectedTransaction(null);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : 'Failed to update transaction';
      setError(errorMessage);
    }
  };

  const handleDeleteTransaction = async () => {
    if (!selectedTransaction) return;

    try {
      await deleteTransaction(selectedTransaction.id);
      setShowDeleteConfirm(false);
      setSelectedTransaction(null);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : 'Failed to delete transaction';
      setError(errorMessage);
    }
  };

  const renderTransactionsList = () => {
    if (isLoading) {
      return (
        <div className="space-y-4 p-4">
          {[...Array(5)].map((_, index) => (
            <div key={index} className="animate-pulse flex justify-between items-center">
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 rounded w-48"></div>
                <div className="h-3 bg-gray-200 rounded w-32"></div>
              </div>
              <div className="h-4 bg-gray-200 rounded w-24"></div>
            </div>
          ))}
        </div>
      );
    }

    if (fetchError) {
      return (
        <div className="p-4">
          <Alert variant="destructive">
            <AlertDescription>
              Error loading transactions: {fetchError.message}
            </AlertDescription>
          </Alert>
        </div>
      );
    }

    if (!transactions || transactions.length === 0) {
      return (
        <div className="text-center text-gray-500 py-8">
          No transactions found
        </div>
      );
    }

    return (
      <div className="divide-y">
        {transactions.map((transaction) => (
          <div
            key={transaction.id}
            className="flex justify-between items-center p-4 hover:bg-gray-50"
          >
            <div className="flex flex-col">
              <span className="font-medium">
                {transaction.description || 'Unnamed Transaction'}
              </span>
              <span className="text-sm text-gray-500">
                {formatDate(transaction.created_at)}
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <span className={`font-medium ${
                transaction.amount >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {formatCurrency(transaction.amount)}
              </span>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSelectedTransaction(transaction);
                    setIsEditModalOpen(true);
                  }}
                >
                  Edit
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => {
                    setSelectedTransaction(transaction);
                    setShowDeleteConfirm(true);
                  }}
                >
                  Delete
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Transactions</h1>
        <div className="flex items-center space-x-4">
          <div className="w-[180px]">
            <Select
              value={selectedAccountId || 'all'}
              onValueChange={(value) => setSelectedAccountId(value === 'all' ? undefined : value)}
            >
              <SelectTrigger>
                <SelectValue defaultValue="all">
                  {selectedAccountId ?
                    accounts.find(account => account.id === selectedAccountId)?.account_name || 'All Accounts'
                    : 'All Accounts'}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Accounts</SelectItem>
                {accounts.map((account) => (
                  <SelectItem key={account.id} value={account.id}>
                    {account.account_name || account.account_identifier}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <Button variant="outline" className="flex items-center gap-2">
            <Filter className="h-4 w-4" /> Filters
          </Button>

          <Button
            className="flex items-center gap-2"
            onClick={() => setIsAddModalOpen(true)}
          >
            <Plus className="h-4 w-4" /> Add Transaction
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex justify-between items-center">
            <span>Recent Transactions</span>
            <span className="text-sm font-normal text-gray-500">
              Total: {total || 0} transactions
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {renderTransactionsList()}
        </CardContent>
      </Card>

      <AddTransactionModal
        isOpen={isAddModalOpen}
        onOpenChange={setIsAddModalOpen}
        onSubmit={handleCreateTransaction}
        accounts={accounts}
        isLoading={isCreating}
      />

      {selectedTransaction && (
        <>
          <EditTransactionModal
            isOpen={isEditModalOpen}
            onOpenChange={setIsEditModalOpen}
            onSubmit={handleUpdateTransaction}
            transaction={selectedTransaction}
            isLoading={isUpdating}
          />

          <ConfirmDialog
            open={showDeleteConfirm}
            onOpenChange={setShowDeleteConfirm}
            title="Delete Transaction"
            description="Are you sure you want to delete this transaction? This action cannot be undone."
            onConfirm={handleDeleteTransaction}
          />
        </>
      )}
    </div>
  );
};

export default TransactionsPage;