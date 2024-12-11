import { render, screen } from '@testing-library/react';
import AccountsPage from '../AccountsPage';
import { mockBankAccount } from '../../test/utils';

describe('AccountsPage', () => {
  it('renders loading state', () => {
    render(<AccountsPage isLoading={true} />);
    expect(screen.getByRole('heading', { name: /accounts/i })).toBeInTheDocument();
    // Look for loading indicator (the animate-pulse div)
    expect(document.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('renders empty state', () => {
    render(<AccountsPage accounts={[]} />);
    expect(screen.getByText(/no connected bank accounts/i)).toBeInTheDocument();
  });

  it('renders accounts list', () => {
    render(<AccountsPage accounts={[mockBankAccount]} />);
    expect(screen.getByText(mockBankAccount.account_name)).toBeInTheDocument();
    expect(screen.getByText(mockBankAccount.account_identifier)).toBeInTheDocument();
  });
});