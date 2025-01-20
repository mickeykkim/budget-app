// src/test/mocks/handlers.ts
import { http, HttpResponse } from 'msw';
import { mockUser, mockBankAccount } from '../utils';

export const handlers = [
  // Simplified login handler
  http.post('/api/v1/auth/login', async () => {
    return HttpResponse.json({
      access_token: 'fake-token',
      token_type: 'bearer'
    });
  }),

  // Simplified user info handler
  http.get('/api/v1/auth/me', () => {
    return HttpResponse.json(mockUser);
  }),

  // Simplified bank accounts handler
  http.get('/api/v1/bank-accounts', () => {
    return HttpResponse.json({
      items: [mockBankAccount],
      total: 1
    });
  })
];