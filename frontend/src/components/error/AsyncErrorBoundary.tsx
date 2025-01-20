// src/components/error/AsyncErrorBoundary.tsx
import React, { Suspense } from 'react';
import { ErrorBoundary } from './ErrorBoundary';

interface AsyncErrorBoundaryProps {
    children: React.ReactNode;
    fallback?: React.ReactNode;
    loadingFallback?: React.ReactNode;
}

const DefaultLoadingFallback = () => (
    <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
    </div>
);

export const AsyncErrorBoundary: React.FC<AsyncErrorBoundaryProps> = ({
    children,
    fallback,
    loadingFallback = <DefaultLoadingFallback />
}) => {
    return (
        <ErrorBoundary fallback={fallback}>
            <Suspense fallback={loadingFallback}>{children}</Suspense>
        </ErrorBoundary>
    );
};