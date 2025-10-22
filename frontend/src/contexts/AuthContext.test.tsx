import React from 'react';
import { render, screen } from '@testing-library/react';
import { AuthProvider } from './AuthContext';

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() }
    }
  })),
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn()
}));

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
