import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the AuthContext
jest.mock('./contexts/AuthContext', () => ({
  useAuth: () => ({
    user: null,
    login: jest.fn(),
    logout: jest.fn(),
    register: jest.fn(),
    loading: false
  })
}));

test('renders app without crashing', () => {
  render(<App />);
  // Basic test to ensure the app renders without errors
  expect(document.body).toBeInTheDocument();
});
