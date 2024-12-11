import { http, HttpResponse } from 'msw';

export const handlers = [
  // Successful login
  http.post('/api/v1/auth/login', async ({ request }) => {
    const formData = await request.text();
    if (formData.includes('test@example.com')) {
      return HttpResponse.json({
        access_token: 'fake-token',
        token_type: 'bearer'
      });
    }
    return HttpResponse.json(
      { detail: 'Incorrect email or password' },
      { status: 401 }
    );
  }),

  http.get('/api/v1/auth/me', () => {
    return HttpResponse.json({
      id: '123',
      email: 'test@example.com',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    });
  })
];