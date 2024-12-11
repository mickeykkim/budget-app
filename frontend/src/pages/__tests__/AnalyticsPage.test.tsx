import { render, screen } from '@testing-library/react';
import AnalyticsPage from '../AnalyticsPage';

describe('AnalyticsPage', () => {
  it('renders analytics page', () => {
    render(<AnalyticsPage />);
    expect(screen.getByRole('heading', { name: /analytics/i })).toBeInTheDocument();
    expect(screen.getByText(/spending analytics and reports/i)).toBeInTheDocument();
  });
});