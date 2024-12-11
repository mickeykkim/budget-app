// src/test/smoke.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { renderWithProviders } from './helpers';

describe('Testing Setup', () => {
  it('renders without crashing', () => {
    render(<div>Test Setup Working</div>);
    expect(screen.getByText('Test Setup Working')).toBeInTheDocument();
  });

  it('works with test wrapper', () => {
    renderWithProviders(<div>Wrapped Test</div>);
    expect(screen.getByText('Wrapped Test')).toBeInTheDocument();
  });
});