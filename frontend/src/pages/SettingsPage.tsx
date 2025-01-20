import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>
      <Card>
        <CardContent className="p-6">
          <p className="text-gray-500">Account settings and preferences will appear here</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default SettingsPage;