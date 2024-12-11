import React from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Home, CreditCard, PieChart, Settings, LogOut } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const MainLayout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Budget App</h1>
            </div>
            <div className="flex items-center">
              <button 
                onClick={handleLogout}
                className="p-2 rounded-md text-gray-400 hover:text-gray-500"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="flex h-[calc(100vh-4rem)]">
        <aside className="w-64 bg-white border-r">
          <nav className="mt-5 px-2">
            <Link
              to="/dashboard"
              className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                isActive('/dashboard')
                  ? 'text-gray-900 bg-gray-100'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Home className="mr-3 h-5 w-5 text-gray-500" />
              Dashboard
            </Link>
            <Link
              to="/accounts"
              className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                isActive('/accounts')
                  ? 'text-gray-900 bg-gray-100'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <CreditCard className="mr-3 h-5 w-5 text-gray-500" />
              Accounts
            </Link>
            <Link
              to="/analytics"
              className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                isActive('/analytics')
                  ? 'text-gray-900 bg-gray-100'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <PieChart className="mr-3 h-5 w-5 text-gray-500" />
              Analytics
            </Link>
            <Link
              to="/settings"
              className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                isActive('/settings')
                  ? 'text-gray-900 bg-gray-100'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Settings className="mr-3 h-5 w-5 text-gray-500" />
              Settings
            </Link>
          </nav>
        </aside>

        <main role="main" className="flex-1 overflow-auto bg-gray-50 p-8">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default MainLayout;