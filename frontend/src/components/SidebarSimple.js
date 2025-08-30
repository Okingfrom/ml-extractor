import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Home, 
  Upload, 
  FileText, 
  User, 
  LogOut,
  Menu,
  ShoppingBag
} from 'lucide-react';
import { clsx } from 'clsx';

const SidebarSimple = ({ expanded, onToggle }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Simplified navigation - only essential items
  const navigationItems = [
    {
      name: 'Inicio',
      href: '/dashboard',
      icon: Home,
      description: 'Panel principal'
    },
    {
      name: 'Subir Archivo',
      href: '/upload',
      icon: Upload,
      description: 'Cargar productos'
    },
    {
      name: 'Mis Archivos',
      href: '/files',
      icon: FileText,
      description: 'Ver resultados'
    },
    {
      name: 'Mi Cuenta',
      href: '/profile',
      icon: User,
      description: 'Configuración'
    }
  ];

  return (
    <>
      {/* Desktop Sidebar */}
      <div 
        className={clsx(
          'fixed left-0 top-0 h-full bg-white shadow-lg border-r border-gray-200 transition-all duration-300 z-40',
          'hidden lg:block',
          expanded ? 'w-64' : 'w-16'
        )}
      >
        {/* Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
          <div className={clsx(
            'flex items-center space-x-3 transition-opacity duration-200',
            expanded ? 'opacity-100' : 'opacity-0'
          )}>
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <ShoppingBag className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg text-gray-900">
              ML Converter
            </span>
          </div>
          
          <button
            onClick={onToggle}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <Menu className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* User Info */}
        {expanded && (
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">
                  {user?.first_name?.charAt(0)?.toUpperCase() || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm text-gray-900 truncate">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-xs text-gray-500">
                  Convierte tus productos fácilmente
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center space-x-3 px-3 py-3 rounded-lg transition-colors group relative',
                    isActive
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )
                }
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                
                <span 
                  className={clsx(
                    'font-medium transition-opacity duration-200',
                    expanded ? 'opacity-100' : 'opacity-0'
                  )}
                >
                  {item.name}
                </span>

                {/* Tooltip for collapsed state */}
                {!expanded && (
                  <div className="absolute left-full ml-2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-50">
                    {item.name}
                    <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-gray-900 rotate-45"></div>
                  </div>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Logout Button */}
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={handleLogout}
            className={clsx(
              'flex items-center space-x-3 px-3 py-3 rounded-lg transition-colors text-gray-600 hover:bg-red-50 hover:text-red-700 w-full group relative'
            )}
          >
            <LogOut className="w-5 h-5 flex-shrink-0" />
            
            <span 
              className={clsx(
                'font-medium transition-opacity duration-200',
                expanded ? 'opacity-100' : 'opacity-0'
              )}
            >
              Salir
            </span>

            {/* Tooltip for collapsed state */}
            {!expanded && (
              <div className="absolute left-full ml-2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-50">
                Salir
                <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-gray-900 rotate-45"></div>
              </div>
            )}
          </button>
        </div>
      </div>

      {/* Mobile Sidebar */}
      <div 
        className={clsx(
          'fixed inset-0 z-50 lg:hidden transition-all duration-300',
          expanded ? 'visible opacity-100' : 'invisible opacity-0'
        )}
      >
        {/* Backdrop */}
        <div 
          className="absolute inset-0 bg-black bg-opacity-50"
          onClick={onToggle}
        />
        
        {/* Mobile Sidebar Panel */}
        <div 
          className={clsx(
            'absolute left-0 top-0 h-full w-80 bg-white shadow-xl transition-transform duration-300',
            expanded ? 'transform-none' : '-translate-x-full'
          )}
        >
          {/* Mobile Header */}
          <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <ShoppingBag className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-lg text-gray-900">
                ML Converter
              </span>
            </div>
            
            <button
              onClick={onToggle}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Menu className="w-5 h-5 text-gray-600" />
            </button>
          </div>

          {/* Mobile User Info */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">
                  {user?.first_name?.charAt(0)?.toUpperCase() || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm text-gray-900 truncate">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-xs text-gray-500">
                  Convierte tus productos fácilmente
                </p>
              </div>
            </div>
          </div>

          {/* Mobile Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  onClick={onToggle} // Close sidebar when navigating on mobile
                  className={({ isActive }) =>
                    clsx(
                      'flex items-center space-x-3 px-3 py-3 rounded-lg transition-colors',
                      isActive
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    )
                  }
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  <span className="font-medium">{item.name}</span>
                </NavLink>
              );
            })}
          </nav>

          {/* Mobile Logout Button */}
          <div className="p-4 border-t border-gray-200">
            <button
              onClick={handleLogout}
              className="flex items-center space-x-3 px-3 py-3 rounded-lg transition-colors text-gray-600 hover:bg-red-50 hover:text-red-700 w-full"
            >
              <LogOut className="w-5 h-5 flex-shrink-0" />
              <span className="font-medium">Salir</span>
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default SidebarSimple;
