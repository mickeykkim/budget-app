import React from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { useForm } from '@/hooks/useForm';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface AddAccountModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: CreateBankAccountData) => Promise<void>;
  isLoading?: boolean;
}

const accountTypes = [
  { value: 'checking', label: 'Checking' },
  { value: 'savings', label: 'Savings' },
  { value: 'credit', label: 'Credit Card' },
  { value: 'investment', label: 'Investment' },
];

const validationRules = {
  account_type: (value: string) =>
    !value ? 'Account type is required' : null,

  access_token: (value: string) =>
    !value ? 'Access token is required' : null,
};

export function AddAccountModal({ isOpen, onOpenChange, onSubmit, isLoading }: AddAccountModalProps) {
  const {
    values,
    errors,
    handleChange,
    resetForm,
  } = useForm(
    {
      account_type: '',
      account_name: '',
      account_identifier: '',
      access_token: '',
      refresh_token: '',
      token_expires_at: '',
    },
    validationRules
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Create a new object with only the filled fields
    const submitData: any = {
      account_type: values.account_type,
      access_token: values.access_token,
    };

    // Only add optional fields if they have values
    if (values.account_name) submitData.account_name = values.account_name;
    if (values.account_identifier) submitData.account_identifier = values.account_identifier;
    if (values.refresh_token) submitData.refresh_token = values.refresh_token;
    if (values.token_expires_at) {
      submitData.token_expires_at = values.token_expires_at;
    }

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
              Add New Account
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
                <label htmlFor="account_type" className="block text-sm font-medium text-gray-700">
                  Account Type*
                </label>
                <select
                  id="account_type"
                  name="account_type"
                  value={values.account_type}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                >
                  <option value="">Select an account type</option>
                  {accountTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
                {errors.account_type && (
                  <p className="mt-1 text-sm text-red-600">{errors.account_type}</p>
                )}
              </div>

              <div>
                <label htmlFor="account_name" className="block text-sm font-medium text-gray-700">
                  Account Name (Optional)
                </label>
                <input
                  id="account_name"
                  name="account_name"
                  type="text"
                  value={values.account_name}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  placeholder="e.g., Primary Checking"
                />
              </div>

              <div>
                <label htmlFor="account_identifier" className="block text-sm font-medium text-gray-700">
                  Account Identifier (Optional)
                </label>
                <input
                  id="account_identifier"
                  name="account_identifier"
                  type="text"
                  value={values.account_identifier}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  placeholder="Last 4 digits of account"
                />
              </div>

              <div>
                <label htmlFor="access_token" className="block text-sm font-medium text-gray-700">
                  Access Token*
                </label>
                <input
                  id="access_token"
                  name="access_token"
                  type="password"
                  value={values.access_token}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  required
                />
                {errors.access_token && (
                  <p className="mt-1 text-sm text-red-600">{errors.access_token}</p>
                )}
              </div>

              <div>
                <label htmlFor="refresh_token" className="block text-sm font-medium text-gray-700">
                  Refresh Token (Optional)
                </label>
                <input
                  id="refresh_token"
                  name="refresh_token"
                  type="password"
                  value={values.refresh_token}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                />
              </div>

              <div>
                <label htmlFor="token_expires_at" className="block text-sm font-medium text-gray-700">
                  Token Expiration (Optional)
                </label>
                <div className="flex space-x-4">
                  <input
                    type="date"
                    id="token_expires_date"
                    name="token_expires_date"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    min={new Date().toISOString().split('T')[0]}
                    onChange={(e) => {
                      const date = e.target.value;
                      const time = (document.getElementById('token_expires_time') as HTMLInputElement)?.value || '23:59';
                      handleChange({
                        target: {
                          name: 'token_expires_at',
                          value: date ? `${date}T${time}` : ''
                        }
                      } as any);
                    }}
                  />
                  <input
                    type="time"
                    id="token_expires_time"
                    name="token_expires_time"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    defaultValue="23:59"
                    onChange={(e) => {
                      const time = e.target.value;
                      const date = (document.getElementById('token_expires_date') as HTMLInputElement)?.value;
                      if (date) {
                        handleChange({
                          target: {
                            name: 'token_expires_at',
                            value: `${date}T${time}`
                          }
                        } as any);
                      }
                    }}
                  />
                </div>
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
                {isLoading ? 'Creating...' : 'Create Account'}
              </Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}