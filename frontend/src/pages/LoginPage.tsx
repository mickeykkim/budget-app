// src/pages/LoginPage.tsx
import React from 'react';
import { LoginForm } from '../features/auth/LoginForm';

const LoginPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <LoginForm />
    </div>
  );
};

export default LoginPage;