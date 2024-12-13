import React, { useState, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useTransactions } from '@/hooks/useTransactions';
import { formatCurrency } from '@/utils/formatting';
import { AlertCircle } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const TIME_RANGES = [
  { label: 'Last 7 Days', value: '7d' },
  { label: 'Last 30 Days', value: '30d' },
  { label: 'This Month', value: 'this-month' },
  { label: 'Last Month', value: 'last-month' },
  { label: 'This Year', value: 'this-year' },
  { label: 'All Time', value: 'all' },
];

const AnalyticsDashboard = () => {
  const [timeRange, setTimeRange] = useState('30d');

  // Calculate date range based on selected time range
  const dateRange = useMemo(() => {
    const now = new Date();
    const ranges = {
      '7d': {
        startDate: new Date(now.setDate(now.getDate() - 7)),
        endDate: new Date()
      },
      '30d': {
        startDate: new Date(now.setDate(now.getDate() - 30)),
        endDate: new Date()
      },
      'this-month': {
        startDate: new Date(now.getFullYear(), now.getMonth(), 1),
        endDate: new Date()
      },
      'last-month': {
        startDate: new Date(now.getFullYear(), now.getMonth() - 1, 1),
        endDate: new Date(now.getFullYear(), now.getMonth(), 0)
      },
      'this-year': {
        startDate: new Date(now.getFullYear(), 0, 1),
        endDate: new Date()
      },
      'all': {
        startDate: null,
        endDate: null
      }
    };
    return ranges[timeRange] || ranges['30d'];
  }, [timeRange]);

  const { transactions, isLoading, error } = useTransactions({
    startDate: dateRange.startDate,
    endDate: dateRange.endDate
  });

  const monthlyData = useMemo(() => {
    if (!transactions) return [];

    const monthlyTotals = transactions.reduce((acc, transaction) => {
      const date = new Date(transaction.created_at);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;

      if (!acc[monthKey]) {
        acc[monthKey] = {
          month: monthKey,
          income: 0,
          expenses: 0,
          balance: 0
        };
      }

      const amount = Number(transaction.amount);
      if (amount >= 0) {
        acc[monthKey].income += amount;
      } else {
        acc[monthKey].expenses += Math.abs(amount);
      }
      acc[monthKey].balance += amount;

      return acc;
    }, {});

    return Object.values(monthlyTotals).sort((a, b) => a.month.localeCompare(b.month));
  }, [transactions]);

  const summaryStats = useMemo(() => {
    if (!transactions) return { income: 0, expenses: 0, balance: 0 };

    return transactions.reduce((acc, transaction) => {
      const amount = Number(transaction.amount);
      if (amount >= 0) {
        acc.income += amount;
      } else {
        acc.expenses += Math.abs(amount);
      }
      acc.balance += amount;
      return acc;
    }, { income: 0, expenses: 0, balance: 0 });
  }, [transactions]);

  const formatTooltipDate = (label: string) => {
    const [year, month] = label.split('-');
    return new Date(Number(year), Number(month) - 1)
      .toLocaleDateString('default', { month: 'long', year: 'numeric' });
  };

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>Failed to load analytics: {error.message}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Select time range" />
          </SelectTrigger>
          <SelectContent>
            {TIME_RANGES.map(({ label, value }) => (
              <SelectItem key={value} value={value}>{label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="p-6">
            <div className="text-sm font-medium text-gray-500">Total Income</div>
            <div className="text-2xl font-bold text-green-600">
              {isLoading ? '...' : formatCurrency(summaryStats.income)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-sm font-medium text-gray-500">Total Expenses</div>
            <div className="text-2xl font-bold text-red-600">
              {isLoading ? '...' : formatCurrency(summaryStats.expenses)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-sm font-medium text-gray-500">Current Balance</div>
            <div className="text-2xl font-bold">
              {isLoading ? '...' : formatCurrency(summaryStats.balance)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Monthly Income vs Expenses Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Monthly Income vs Expenses</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            {isLoading ? (
              <div className="h-full flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
              </div>
            ) : (
              <ResponsiveContainer>
                <BarChart data={monthlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="month"
                    tickFormatter={formatTooltipDate}
                  />
                  <YAxis tickFormatter={formatCurrency} />
                  <Tooltip
                    formatter={(value) => formatCurrency(Number(value))}
                    labelFormatter={formatTooltipDate}
                  />
                  <Bar dataKey="income" name="Income" fill="#4CAF50" />
                  <Bar dataKey="expenses" name="Expenses" fill="#FF5252" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Balance Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Balance Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            {isLoading ? (
              <div className="h-full flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
              </div>
            ) : (
              <ResponsiveContainer>
                <LineChart data={monthlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="month"
                    tickFormatter={formatTooltipDate}
                  />
                  <YAxis tickFormatter={formatCurrency} />
                  <Tooltip
                    formatter={(value) => formatCurrency(Number(value))}
                    labelFormatter={formatTooltipDate}
                  />
                  <Line
                    type="monotone"
                    dataKey="balance"
                    name="Balance"
                    stroke="#2196F3"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AnalyticsDashboard;