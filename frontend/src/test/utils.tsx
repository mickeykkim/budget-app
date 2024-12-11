// src/test/utils.tsx
import { ReactNode } from 'react';
import { render as rtlRender, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthContext } from '../context/AuthContext';

// Test data mocks
export const mockUser = {
  id: '123',
  email: 'test@example.com'
};

export const mockBankAccount = {
  id: '456',
  account_type: 'checking',
  account_name: 'Main Account',
  account_identifier: '****1234'
};

export const mockAuthResponse = {
  access_token: 'fake-token',
  token_type: 'bearer'
};

// Default auth value for testing
export const defaultAuthValue = {
  user: mockUser,
  token: 'test-token',
  login: vi.fn(),
  logout: vi.fn(),
  isLoading: false
};

// Storage mock
export function mockLocalStorage() {
  const store: { [key: string]: string } = {};
  
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      Object.keys(store).forEach(key => delete store[key]);
    }
  };
}

// Types for render options
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  route?: string;
  initialEntries?: string[];
  withAuth?: boolean;
  withQuery?: boolean;
  authValue?: typeof defaultAuthValue;
}

// Create a custom render function
export function renderWithProviders(
  ui: React.ReactElement,
  {
    route = '/',
    initialEntries = [route],
    withAuth = true,
    withQuery = true,
    authValue = defaultAuthValue,
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
    },
    logger: {
      log: console.log,
      warn: console.warn,
      error: () => {},
    },
  });

  function Wrapper({ children }: { children: ReactNode }) {
    let wrappedChildren = children;

    if (withAuth) {
      wrappedChildren = (
        <AuthProvider>{wrappedChildren}</AuthProvider>
      );
    }

    if (withQuery) {
      wrappedChildren = (
        <QueryClientProvider client={queryClient}>
          {wrappedChildren}
        </QueryClientProvider>
      );
    }

    return (
      <BrowserRouter>
        {wrappedChildren}
      </BrowserRouter>
    );
  }

  return {
    ...rtlRender(ui, { wrapper: Wrapper, ...renderOptions }),
    queryClient,
  };
}

// Helper to simulate waiting for async operations
export const waitForAsync = () => new Promise(resolve => setTimeout(resolve, 0));

// Re-export everything from testing-library
export * from '@testing-library/react';