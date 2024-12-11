import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import LocalStackStatus from '../components/LocalStackStatus';

interface DashboardStats {
  totalBalance: number;
  monthlySpending: number;
  monthlyIncome: number;
}

const DashboardPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <LocalStackStatus />
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <h2 className="text-sm font-medium text-gray-500">Total Balance</h2>
            <p className="mt-2 text-3xl font-semibold">$0.00</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <h2 className="text-sm font-medium text-gray-500">Monthly Spending</h2>
            <p className="mt-2 text-3xl font-semibold">$0.00</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <h2 className="text-sm font-medium text-gray-500">Monthly Income</h2>
            <p className="mt-2 text-3xl font-semibold">$0.00</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;
