import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

const AnalyticsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Analytics</h1>
      <Card>
        <CardContent className="p-6">
          <p className="text-gray-500">Spending analytics and reports will appear here</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default AnalyticsPage;