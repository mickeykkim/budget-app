import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import App from './App';

// Mock the AuthContext
vi.mock('./context/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => children,
  useAuth: () => ({
    token: 'fake-token',
    user: {
      email: 'test@example.com'
    },
    login: vi.fn(),
    logout: vi.fn(),
    isLoading: false
  }),
  ProtectedRoute: ({ children }: { children: React.ReactNode }) => children,
}));

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />);
    expect(document.querySelector('div')).toBeInTheDocument();
  });

  it('contains main navigation routes', () => {
    render(<App />);
    const dashboardLink = screen.getByRole('link', { name: /dashboard/i });
    const accountsLink = screen.getByRole('link', { name: /accounts/i });
    const analyticsLink = screen.getByRole('link', { name: /analytics/i });
    const settingsLink = screen.getByRole('link', { name: /settings/i });
    
    expect(dashboardLink).toBeInTheDocument();
    expect(accountsLink).toBeInTheDocument();
    expect(analyticsLink).toBeInTheDocument();
    expect(settingsLink).toBeInTheDocument();
  });
});