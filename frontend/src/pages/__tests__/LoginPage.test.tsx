import { render } from '@testing-library/react';
import LoginPage from '../LoginPage';
import { vi } from 'vitest';

// Mock LoginForm component
vi.mock('../../features/auth/LoginForm', () => ({
  LoginForm: () => <div data-testid="login-form">Login Form</div>
}));

describe('LoginPage', () => {
  it('renders login form', () => {
    const { getByTestId } = render(<LoginPage />);
    expect(getByTestId('login-form')).toBeInTheDocument();
  });
});