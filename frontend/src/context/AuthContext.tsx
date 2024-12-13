import React, { createContext, useContext, useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { api } from '@/lib/api';
import { User } from '@/types';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  login: async () => {},
  logout: () => {}
});

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchUser();
    }
  }, []);

  const fetchUser = async () => {
    try {
      const userData = await api.get('/auth/me');
      setUser(userData);
      setIsAuthenticated(true);
    } catch {
      logout();
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const { access_token } = await api.login(email, password);
      localStorage.setItem('access_token', access_token);
      await fetchUser();
    } catch (error) {
      logout();
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};