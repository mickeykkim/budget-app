import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Calendar } from 'lucide-react';

interface DateRangeProps {
  startDate: Date | null;
  endDate: Date | null;
  onRangeChange: (range: { startDate: Date | null; endDate: Date | null }) => void;
}

const PREDEFINED_RANGES = [
  { label: 'Last 7 Days', value: '7d' },
  { label: 'Last 30 Days', value: '30d' },
  { label: 'This Month', value: 'this-month' },
  { label: 'Last Month', value: 'last-month' },
  { label: 'This Year', value: 'this-year' },
  { label: 'Last Year', value: 'last-year' },
  { label: 'All Time', value: 'all' },
] as const;

export const DateRangeSelector = ({ startDate, endDate, onRangeChange }: DateRangeProps) => {
  const handleRangeSelect = (value: string) => {
    const now = new Date();
    let start: Date | null = null;
    let end: Date | null = null;

    switch (value) {
      case '7d':
        start = new Date(now.setDate(now.getDate() - 7));
        end = new Date();
        break;
      case '30d':
        start = new Date(now.setDate(now.getDate() - 30));
        end = new Date();
        break;
      case 'this-month':
        start = new Date(now.getFullYear(), now.getMonth(), 1);
        end = new Date();
        break;
      case 'last-month':
        start = new Date(now.getFullYear(), now.getMonth() - 1, 1);
        end = new Date(now.getFullYear(), now.getMonth(), 0);
        break;
      case 'this-year':
        start = new Date(now.getFullYear(), 0, 1);
        end = new Date();
        break;
      case 'last-year':
        start = new Date(now.getFullYear() - 1, 0, 1);
        end = new Date(now.getFullYear() - 1, 11, 31);
        break;
      case 'all':
        start = null;
        end = null;
        break;
    }

    onRangeChange({ startDate: start, endDate: end });
  };

  const formatDate = (date: Date | null) => {
    if (!date) return '';
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getCurrentRangeLabel = () => {
    if (!startDate && !endDate) return 'All Time';
    return `${formatDate(startDate)} - ${formatDate(endDate)}`;
  };

  return (
    <div className="flex items-center space-x-2">
      <Select onValueChange={handleRangeSelect}>
        <SelectTrigger className="w-48">
          <Calendar className="w-4 h-4 mr-2" />
          <SelectValue placeholder={getCurrentRangeLabel()} />
        </SelectTrigger>
        <SelectContent>
          {PREDEFINED_RANGES.map(({ label, value }) => (
            <SelectItem key={value} value={value}>
              {label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {(startDate || endDate) && (
        <Button
          variant="outline"
          size="sm"
          onClick={() => onRangeChange({ startDate: null, endDate: null })}
        >
          Clear
        </Button>
      )}
    </div>
  );
};