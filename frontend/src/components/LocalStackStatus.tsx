import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { AlertCircle, CheckCircle, MinusCircle } from 'lucide-react';

const SUPPORTED_SERVICES = [
  'apigateway',
  'cloudwatch',
  'ec2',
  'events',
  'iam',
  'lambda',
  's3',
  'sqs',
  'sts'
];

const SERVICE_LABELS: { [key: string]: string } = {
  apigateway: 'API Gateway',
  cloudwatch: 'CloudWatch',
  ec2: 'EC2',
  events: 'EventBridge',
  iam: 'IAM',
  lambda: 'Lambda',
  s3: 'S3',
  sqs: 'SQS',
  sts: 'STS'
};

interface ServiceStatus {
  [key: string]: string;
}

const LocalStackStatus = () => {
  const [status, setStatus] = useState<ServiceStatus>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch('/api/v1/aws/localstack-health');
        if (!response.ok) {
          throw new Error('Failed to fetch LocalStack status');
        }
        
        const data = await response.json();
        
        if (data.error) {
          throw new Error(data.error);
        }
        
        // Filter only supported services and their status
        const serviceStatus = Object.entries(data.services)
          .filter(([service]) => SUPPORTED_SERVICES.includes(service))
          .reduce((acc, [service, status]) => ({
            ...acc,
            [service]: status
          }), {});
        
        setStatus(serviceStatus);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to connect to LocalStack');
      } finally {
        setLoading(false);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900" />
            <p>Checking LocalStack status...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center text-red-600">
            <AlertCircle className="mr-2 h-5 w-5" />
            LocalStack Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-600">{error}</p>
          <p className="text-xs text-gray-500 mt-2">Make sure LocalStack is running and accessible through the backend proxy.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <span>LocalStack Services</span>
          <span className="ml-2 text-sm font-normal text-gray-500">
            {Object.values(status).filter(s => s === 'available').length} / {SUPPORTED_SERVICES.length} available
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {SUPPORTED_SERVICES.map((service) => {
            const serviceStatus = status[service];
            const isAvailable = serviceStatus === 'available';
            const isDisabled = serviceStatus === 'disabled';
            
            return (
              <div key={service} className="flex items-center space-x-2 p-2 rounded-md bg-gray-50">
                {isAvailable ? (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                ) : isDisabled ? (
                  <MinusCircle className="h-4 w-4 text-gray-400" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-red-500" />
                )}
                <div className="flex flex-col">
                  <span className="text-sm font-medium">
                    {SERVICE_LABELS[service]}
                  </span>
                  <span className="text-xs text-gray-500">
                    {isAvailable ? 'Available' : isDisabled ? 'Disabled' : 'Error'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default LocalStackStatus;