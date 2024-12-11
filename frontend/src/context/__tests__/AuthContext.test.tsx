// src/context/AuthContext.test.tsx
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider, useAuth, ProtectedRoute } from '../AuthContext';
import { mockUser } from '../test/testUtils';

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  const TestComponent = () => {
    const { token, user, login, logout } = useAuth();
    return (
      <div>
        <div data-testid="token">{token || 'no token'}</div>
        <div data-testid="user">{user?.email || 'no user'}</div>
        <button onClick={() => login('test-token')}>Login</button>
        <button onClick={logout}>Logout</button>
      </div>
    );
  };

  const renderWithAuth = () => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  it('provides authentication state to children', async () => {
    renderWithAuth();
    
    await waitFor(() => {
      expect(screen.getByTestId('token')).toHaveTextContent('no token');
      expect(screen.getByTestId('user')).toHaveTextContent('no user');
    });
  });

  it('handles login successfully', async () => {
    const user = userEvent.setup();
    renderWithAuth();

    await act(async () => {
      await user.click(screen.getByText('Login'));
    });

    await waitFor(() => {
      expect(localStorage.getItem('token')).toBe('test-token');
      expect(screen.getByTestId('token')).toHaveTextContent('test-token');
    });
  });

  it('handles logout successfully', async () => {
    const user = userEvent.setup();
    localStorage.setItem('token', 'test-token');
    renderWithAuth();

    await act(async () => {
      await user.click(screen.getByText('Logout'));
    });

    await waitFor(() => {
      expect(localStorage.getItem('token')).toBeNull();
      expect(screen.getByTestId('token')).toHaveTextContent('no token');
    });
  });

  describe('ProtectedRoute', () => {
    const mockNavigate = vi.fn();
    
    beforeEach(() => {
      vi.mock('react-router-dom', async () => {
        const actual = await vi.importActual('react-router-dom');
        return {
          ...actual,
          useNavigate: () => mockNavigate,
          useLocation: () => ({ pathname: '/test' })
        };
      });
    });

    it('redirects to login when not authenticated', async () => {
      render(
        <BrowserRouter>
          <AuthProvider>
            <ProtectedRoute>
              <div>Protected Content</div>
            </ProtectedRoute>
          </AuthProvider>
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(window.location.pathname).toBe('/login');
      });
    });

    it('renders children when authenticated', async () => {
      localStorage.setItem('token', 'test-token');
      
      render(
        <BrowserRouter>
          <AuthProvider>
            <ProtectedRoute>
              <div>Protected Content</div>
            </ProtectedRoute>
          </AuthProvider>
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Protected Content')).toBeInTheDocument();
      });
    });
  });
});