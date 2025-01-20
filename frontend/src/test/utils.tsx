// src/test/utils.tsx
import { ReactNode } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';

export const mockUser = {
  id: '1',
  email: 'test@example.com',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
};

export const mockBankAccount = {
  id: '1',
  user_id: '1',
  account_type: 'checking',
  account_name: 'Test Account',
  account_identifier: '1234',
  created_at: '2024-01-01T00:00:00Z',
  is_active: true
};

export function renderWithProviders(
  ui: React.ReactElement,
  options: Omit<RenderOptions, 'wrapper'> = {}
) {
  const Wrapper = ({ children }: { children: ReactNode }) => (
    <BrowserRouter>
      {children}
    </BrowserRouter>
  );

  return render(ui, { wrapper: Wrapper, ...options });
}

export * from '@testing-library/react';