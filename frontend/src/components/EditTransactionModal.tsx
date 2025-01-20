import React from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { useForm } from '@/hooks/useForm';
import { Button } from '@/components/ui/button';
import { Transaction, UpdateTransactionData } from '@/types';

interface EditTransactionModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: UpdateTransactionData) => Promise<void>;
  transaction: Transaction;
  isLoading?: boolean;
}

const validationRules = {
  amount: (value: string) => {
    if (!value) return 'Amount is required';
    const num = parseFloat(value);
    if (isNaN(num)) return 'Amount must be a number';
    if (num === 0) return 'Amount cannot be zero';
    return null;
  },

  description: (value: string) =>
    value && value.length > 255 ? 'Description must be less than 255 characters' : null,
};

export function EditTransactionModal({
  isOpen,
  onOpenChange,
  onSubmit,
  transaction,
  isLoading
}: EditTransactionModalProps) {
  const {
    values,
    errors,
    handleChange,
    resetForm,
  } = useForm(
    {
      amount: transaction.amount.toString(),
      description: transaction.description || '',
    },
    validationRules
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const submitData: UpdateTransactionData = {
      amount: parseFloat(values.amount),
      description: values.description || undefined,
    };

    await onSubmit(submitData);
  };

  const handleClose = () => {
    resetForm();
    onOpenChange(false);
  };

  return (
    <Dialog.Root open={isOpen} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50" />
        <Dialog.Content className="fixed top-[50%] left-[50%] translate-x-[-50%] translate-y-[-50%] bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
          <div className="flex justify-between items-center mb-4">
            <Dialog.Title className="text-lg font-semibold">
              Edit Transaction
            </Dialog.Title>
            <Dialog.Close asChild>
              <button className="text-gray-400 hover:text-gray-500">
                <X className="h-4 w-4" />
              </button>
            </Dialog.Close>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div>
                <label htmlFor="amount" className="block text-sm font-medium text-gray-700">
                  Amount* <span className="text-sm text-gray-500">(negative for expenses)</span>
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span className="text-gray-500 sm:text-sm">$</span>
                  </div>
                  <input
                    type="number"
                    name="amount"
                    id="amount"
                    step="0.01"
                    value={values.amount}
                    onChange={handleChange}
                    className="pl-7 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    placeholder="0.00"
                  />
                </div>
                {errors.amount && (
                  <p className="mt-1 text-sm text-red-600">{errors.amount}</p>
                )}
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                  Description (Optional)
                </label>
                <input
                  type="text"
                  name="description"
                  id="description"
                  value={values.description}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  placeholder="e.g., Grocery shopping"
                />
                {errors.description && (
                  <p className="mt-1 text-sm text-red-600">{errors.description}</p>
                )}
              </div>
            </div>

            <div className="mt-6 flex justify-end space-x-3">
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isLoading}
              >
                {isLoading ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}