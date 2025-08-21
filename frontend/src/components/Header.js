import React from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Bell, Search, Menu } from 'lucide-react';

const Header = ({ sidebarExpanded, onSidebarToggle }) => {
  const { user } = useAuth();
  const location = useLocation();

  // Get page title based on current route
  const getPageTitle = () => {
    const path = location.pathname;
    const routes = {
      '/dashboard': 'Dashboard',
      '/upload': 'Subir Archivo',
      '/mapping': 'Configurar Mapeo',
      '/validation': 'Validar Datos',
      '/profile': 'Perfil',
    };
    return routes[path] || 'ML Extractor';
  };

  const getBreadcrumbs = () => {
    const path = location.pathname;
    const segments = path.split('/').filter(Boolean);
    
    if (segments.length === 0) return [{ name: 'Dashboard', href: '/dashboard' }];
    
    const breadcrumbs = [
      { name: 'Inicio', href: '/dashboard' },
    ];
    
    segments.forEach((segment, index) => {
      const href = '/' + segments.slice(0, index + 1).join('/');
      const name = segment.charAt(0).toUpperCase() + segment.slice(1);
      breadcrumbs.push({ name, href });
    });
    
    return breadcrumbs;
  };

  return (
    <header className="h-16 bg-white border-b border-secondary-200 flex items-center justify-between px-6">
      {/* Left Side - Title and Breadcrumbs */}
      <div className="flex items-center space-x-4">
        {/* Mobile Menu Button */}
        <button
          onClick={onSidebarToggle}
          className="lg:hidden p-2 rounded-lg hover:bg-secondary-100 transition-colors"
        >
          <Menu className="w-5 h-5 text-secondary-600" />
        </button>

        <div>
          <h1 className="text-xl font-semibold text-secondary-900">
            {getPageTitle()}
          </h1>
          
          {/* Breadcrumbs */}
          <nav className="flex items-center space-x-1 text-sm text-secondary-500 mt-1">
            {getBreadcrumbs().map((crumb, index) => (
              <React.Fragment key={crumb.href}>
                {index > 0 && <span>/</span>}
                <span className={index === getBreadcrumbs().length - 1 ? 'text-primary-600 font-medium' : ''}>
                  {crumb.name}
                </span>
              </React.Fragment>
            ))}
          </nav>
        </div>
      </div>

      {/* Right Side - Search and Actions */}
      <div className="flex items-center space-x-4">
        {/* Search Bar - Hidden on mobile */}
        <div className="hidden md:flex items-center">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary-400" />
            <input
              type="text"
              placeholder="Buscar..."
              className="pl-10 pr-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent w-64"
            />
          </div>
        </div>

        {/* Notifications */}
        <button className="relative p-2 rounded-lg hover:bg-secondary-100 transition-colors">
          <Bell className="w-5 h-5 text-secondary-600" />
          {/* Notification badge */}
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-error-500 rounded-full"></span>
        </button>

        {/* User Menu */}
        <div className="flex items-center space-x-3">
          <div className="hidden sm:block text-right">
            <p className="text-sm font-medium text-secondary-900">
              {user?.first_name} {user?.last_name}
            </p>
            <p className="text-xs text-secondary-500">
              {user?.email}
            </p>
          </div>
          
          <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
            <span className="text-white font-medium text-sm">
              {user?.first_name?.charAt(0)?.toUpperCase() || 'U'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
