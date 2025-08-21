import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Home, 
  Upload, 
  Settings, 
  CheckSquare, 
  User, 
  LogOut,
  Menu,
  ShoppingBag,
  Zap
} from 'lucide-react';
import { clsx } from 'clsx';

const Sidebar = ({ expanded, onToggle }) => {
  const { user, logout, isPremium } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navigationItems = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: Home,
      description: 'Panel principal'
    },
    {
      name: 'Subir Archivo',
      href: '/upload',
      icon: Upload,
      description: 'Cargar datos'
    },
    {
      name: 'Configurar Mapeo',
      href: '/mapping',
      icon: Settings,
      description: 'Configurar campos'
    },
    {
      name: 'Validar Datos',
      href: '/validation',
      icon: CheckSquare,
      description: 'Revisar información'
    },
    {
      name: 'Perfil',
      href: '/profile',
      icon: User,
      description: 'Configuración de cuenta'
    },
  ];

  return (
    <>
      {/* Desktop Sidebar */}
      <div 
        className={clsx(
          'fixed left-0 top-0 h-full bg-white shadow-xl border-r border-secondary-200 transition-all duration-300 z-40',
          expanded ? 'w-64' : 'w-16'
        )}
      >
        {/* Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-secondary-200">
          <div className={clsx(
            'flex items-center space-x-3 transition-opacity duration-200',
            expanded ? 'opacity-100' : 'opacity-0'
          )}>
            <div className="w-8 h-8 ml-gradient rounded-lg flex items-center justify-center">
              <ShoppingBag className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg text-secondary-900">
              ML Extractor
            </span>
          </div>
          
          <button
            onClick={onToggle}
            className="p-2 rounded-lg hover:bg-secondary-100 transition-colors"
          >
            <Menu className="w-5 h-5 text-secondary-600" />
          </button>
        </div>

        {/* User Info */}
        {expanded && (
          <div className="p-4 border-b border-secondary-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">
                  {user?.first_name?.charAt(0)?.toUpperCase() || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm text-secondary-900 truncate">
                  {user?.first_name} {user?.last_name}
                </p>
                <div className="flex items-center space-x-1">
                  <span className={clsx(
                    'text-xs px-2 py-1 rounded-full font-medium',
                    isPremium 
                      ? 'bg-warning-100 text-warning-800' 
                      : 'bg-secondary-100 text-secondary-600'
                  )}>
                    {isPremium ? 'Premium' : 'Gratuito'}
                  </span>
                  {isPremium && (
                    <Zap className="w-3 h-3 text-warning-600" />
                  )}
                </div>
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
                    'flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors group relative',
                    isActive
                      ? 'bg-primary-50 text-primary-700 border border-primary-200'
                      : 'text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900'
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
                  <div className="absolute left-full ml-2 px-2 py-1 bg-secondary-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-50">
                    {item.name}
                    <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-secondary-900 rotate-45"></div>
                  </div>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Logout Button */}
        <div className="p-4 border-t border-secondary-200">
          <button
            onClick={handleLogout}
            className={clsx(
              'flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors text-secondary-600 hover:bg-error-50 hover:text-error-700 w-full group relative'
            )}
          >
            <LogOut className="w-5 h-5 flex-shrink-0" />
            
            <span 
              className={clsx(
                'font-medium transition-opacity duration-200',
                expanded ? 'opacity-100' : 'opacity-0'
              )}
            >
              Cerrar Sesión
            </span>

            {/* Tooltip for collapsed state */}
            {!expanded && (
              <div className="absolute left-full ml-2 px-2 py-1 bg-secondary-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-50">
                Cerrar Sesión
                <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-secondary-900 rotate-45"></div>
              </div>
            )}
          </button>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
