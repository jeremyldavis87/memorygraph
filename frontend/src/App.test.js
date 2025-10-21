import { render, screen } from '@testing-library/react';
import App from './App';

test('renders MemoryGraph title', () => {
  render(<App />);
  const titleElement = screen.getByText(/MemoryGraph/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders API status', () => {
  render(<App />);
  const statusElement = screen.getByText(/API Status/i);
  expect(statusElement).toBeInTheDocument();
});