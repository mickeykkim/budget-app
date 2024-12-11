import { render, screen } from '@testing-library/react';
import DashboardPage from '../DashboardPage';

describe('DashboardPage', () => {
  it('renders dashboard stats', () => {
    render(<DashboardPage />);
    
    expect(screen.getByText('Total Balance')).toBeInTheDocument();
    expect(screen.getByText('Monthly Spending')).toBeInTheDocument();
    expect(screen.getByText('Monthly Income')).toBeInTheDocument();
  });
});