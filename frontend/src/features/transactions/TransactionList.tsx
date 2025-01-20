import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { useFetch } from '@/hooks/useFetch';
import { formatCurrency, formatDate } from '@/utils/formatting';

interface Transaction {
  id: string;
  amount: number;
  description: string;
  created_at: string;
  bank_account_id: string;
}

export default function TransactionList() {
  const {
    data: transactions,
    loading,
    error
  } = useFetch<{ items: Transaction[] }>('/transactions');

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex justify-between items-center">
                <div className="w-1/4 h-4 bg-gray-200 rounded"></div>
                <div className="w-1/4 h-4 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-red-500">Error loading transactions: {error.message}</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Transactions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {transactions?.items.map((transaction) => (
            <div
              key={transaction.id}
              className="flex justify-between items-center p-4 hover:bg-gray-50 rounded-md transition-colors"
            >
              <div className="flex flex-col">
                <span className="font-medium">{transaction.description}</span>
                <span className="text-sm text-gray-500">
                  {formatDate(transaction.created_at)}
                </span>
              </div>
              <span className={`font-medium ${Number(transaction.amount) >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                {formatCurrency(Number(transaction.amount))}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}