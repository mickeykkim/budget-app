import { render, screen } from '@testing-library/react';
import SettingsPage from '../SettingsPage';

describe('SettingsPage', () => {
  it('renders settings page', () => {
    render(<SettingsPage />);
    expect(screen.getByRole('heading', { name: /settings/i })).toBeInTheDocument();
    expect(screen.getByText(/account settings and preferences/i)).toBeInTheDocument();
  });
});