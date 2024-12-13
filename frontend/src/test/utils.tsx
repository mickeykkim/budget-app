// src/test/utils.tsx
import { ReactNode } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';

// Mock data remains the same

// Simplified render function
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

// Re-export testing library
export * from '@testing-library/react';