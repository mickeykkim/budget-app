// src/context/__tests__/QueryProvider.test.tsx
import { screen } from '@testing-library/react';
import { useQuery } from '@tanstack/react-query';
import { renderWithProviders } from '@/test/utils';

// Test component that uses React Query
function TestComponent() {
  const { data, isLoading } = useQuery({
    queryKey: ['test'],
    queryFn: () => Promise.resolve('test-data'),
  });

  if (isLoading) return <div>Loading...</div>;
  return <div>{data}</div>;
}

describe('Query Integration', () => {
  it('works with query client', async () => {
    renderWithProviders(<TestComponent />, {
      withQuery: true,
      withAuth: false
    });

    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(await screen.findByText('test-data')).toBeInTheDocument();
  });

  // Remove the auth context test since we're primarily testing Query functionality
  it('works with data fetching and caching', async () => {
    const { queryClient } = renderWithProviders(<TestComponent />, {
      withQuery: true,
      withAuth: false
    });

    // Initial render
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(await screen.findByText('test-data')).toBeInTheDocument();

    // Data should be cached
    expect(queryClient.getQueryData(['test'])).toBe('test-data');
  });
});