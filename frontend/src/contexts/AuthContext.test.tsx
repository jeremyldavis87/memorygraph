import React from 'react';
import { render, screen } from '@testing-library/react';
import { AuthProvider } from './AuthContext';

// Mock the auth service
jest.mock('../services/authService', () => ({
  login: jest.fn(),
  register: jest.fn(),
  logout: jest.fn(),
  getCurrentUser: jest.fn()
}));

test('AuthProvider renders children', () => {
  render(
    <AuthProvider>
      <div>Test Child</div>
    </AuthProvider>
  );
  
  expect(screen.getByText('Test Child')).toBeInTheDocument();
});
