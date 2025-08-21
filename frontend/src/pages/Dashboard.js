import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  Upload, 
  FileText, 
  BarChart3, 
  Users, 
  TrendingUp, 
  Clock,
  CheckCircle,
  AlertTriangle,
  Zap,
  Crown
} from 'lucide-react';
import { clsx } from 'clsx';

const Dashboard = () => {
  const { user, isPremium } = useAuth();
  const [stats, setStats] = useState({
    totalUploads: 0,
    successfulProcesses: 0,
    totalErrors: 0,
    recentActivity: [],
  });

  useEffect(() => {
    // Simulate loading stats
    setTimeout(() => {
      setStats({
        totalUploads: 24,
        successfulProcesses: 22,
        totalErrors: 2,
        recentActivity: [
          {
            id: 1,
            type: 'upload',
            title: 'Archivo productos.xlsx procesado',
            time: '2 minutos',
            status: 'success',
          },
          {
            id: 2,
            type: 'mapping',
            title: 'Configuración de mapeo actualizada',
            time: '1 hora',
            status: 'success',
          },
          {
            id: 3,
            type: 'error',
            title: 'Error en archivo datos.csv',
            time: '2 horas',
            status: 'error',
          },
          {
            id: 4,
            type: 'upload',
            title: 'Archivo inventario.xlsx procesado',
            time: '3 horas',
            status: 'success',
          },
        ],
      });
    }, 1000);
  }, []);

  const StatCard = ({ title, value, icon: Icon, color, change }) => (
    <div className="card p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-secondary-600">{title}</p>
          <p className="text-2xl font-bold text-secondary-900 mt-1">{value}</p>
          {change && (
            <p className={clsx(
              'text-sm mt-1 flex items-center',
              change.positive ? 'text-success-600' : 'text-error-600'
            )}>
              <TrendingUp className="w-4 h-4 mr-1" />
              {change.value}% desde ayer
            </p>
          )}
        </div>
        <div className={clsx('w-12 h-12 rounded-lg flex items-center justify-center', color)}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );

  const QuickActionCard = ({ title, description, icon: Icon, color, onClick, disabled = false }) => (
    <button
      onClick={onClick}
      disabled={disabled}
      className={clsx(
        'card p-6 text-left transition-all duration-200 hover:shadow-lg hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <div className="flex items-start space-x-4">
        <div className={clsx('w-10 h-10 rounded-lg flex items-center justify-center', color)}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-secondary-900">{title}</h3>
          <p className="text-sm text-secondary-600 mt-1">{description}</p>
        </div>
      </div>
    </button>
  );

  const ActivityItem = ({ activity }) => {
    const getActivityIcon = () => {
      switch (activity.type) {
        case 'upload':
          return Upload;
        case 'mapping':
          return FileText;
        case 'error':
          return AlertTriangle;
        default:
          return FileText;
      }
    };

    const getActivityColor = () => {
      switch (activity.status) {
        case 'success':
          return 'text-success-600';
        case 'error':
          return 'text-error-600';
        case 'warning':
          return 'text-warning-600';
        default:
          return 'text-secondary-600';
      }
    };

    const Icon = getActivityIcon();

    return (
      <div className="flex items-start space-x-3 p-3 hover:bg-secondary-50 rounded-lg transition-colors">
        <div className={clsx('w-8 h-8 rounded-full flex items-center justify-center', 
          activity.status === 'success' ? 'bg-success-100' : 
          activity.status === 'error' ? 'bg-error-100' : 'bg-secondary-100'
        )}>
          <Icon className={clsx('w-4 h-4', getActivityColor())} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-secondary-900">{activity.title}</p>
          <p className="text-xs text-secondary-500">Hace {activity.time}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="card p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-secondary-900">
              ¡Bienvenido, {user?.first_name}! 👋
            </h1>
            <p className="text-secondary-600 mt-1">
              Aquí tienes un resumen de tu actividad en ML Extractor
            </p>
          </div>
          
          {/* Account Badge */}
          <div className={clsx(
            'flex items-center space-x-2 px-4 py-2 rounded-full text-sm font-medium',
            isPremium 
              ? 'bg-gradient-to-r from-warning-100 to-warning-200 text-warning-800 border border-warning-300' 
              : 'bg-secondary-100 text-secondary-700 border border-secondary-200'
          )}>
            {isPremium ? (
              <>
                <Crown className="w-4 h-4" />
                <span>Cuenta Premium</span>
              </>
            ) : (
              <>
                <Users className="w-4 h-4" />
                <span>Cuenta Gratuita</span>
              </>
            )}
          </div>
        </div>
        
        {/* Upgrade Banner for Free Users */}
        {!isPremium && (
          <div className="mt-4 p-4 bg-gradient-to-r from-primary-50 to-purple-50 border border-primary-200 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-purple-500 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-secondary-900">
                  ¡Desbloquea todo el potencial de ML Extractor!
                </h3>
                <p className="text-sm text-secondary-600 mt-1">
                  Obtén acceso a IA avanzada, procesamiento ilimitado y soporte prioritario.
                </p>
              </div>
              <button className="btn-primary">
                Actualizar a Premium
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Archivos"
          value={stats.totalUploads}
          icon={Upload}
          color="bg-primary-500"
          change={{ value: 12, positive: true }}
        />
        <StatCard
          title="Procesados Exitosamente"
          value={stats.successfulProcesses}
          icon={CheckCircle}
          color="bg-success-500"
          change={{ value: 8, positive: true }}
        />
        <StatCard
          title="Errores"
          value={stats.totalErrors}
          icon={AlertTriangle}
          color="bg-error-500"
        />
        <StatCard
          title="Tiempo Ahorrado"
          value="24h"
          icon={Clock}
          color="bg-purple-500"
          change={{ value: 15, positive: true }}
        />
      </div>

      {/* Quick Actions & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="card-header">
              <h2 className="text-lg font-semibold text-secondary-900">Acciones Rápidas</h2>
              <p className="text-sm text-secondary-600">Comienza a trabajar con tus datos</p>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <QuickActionCard
                  title="Subir Nuevo Archivo"
                  description="Carga un Excel, CSV o PDF para procesar"
                  icon={Upload}
                  color="bg-primary-500"
                  onClick={() => window.location.href = '/upload'}
                />
                <QuickActionCard
                  title="Configurar Mapeo"
                  description="Define cómo mapear tus datos a ML"
                  icon={FileText}
                  color="bg-secondary-500"
                  onClick={() => window.location.href = '/mapping'}
                />
                <QuickActionCard
                  title="Validar Datos"
                  description="Revisa y corrige tus datos antes de exportar"
                  icon={CheckCircle}
                  color="bg-success-500"
                  onClick={() => window.location.href = '/validation'}
                />
                <QuickActionCard
                  title="Análisis con IA"
                  description="Usa IA para mejorar tus descripciones"
                  icon={Zap}
                  color="bg-warning-500"
                  disabled={!isPremium}
                  onClick={() => window.location.href = '/ai-analysis'}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-secondary-900">Actividad Reciente</h2>
          </div>
          <div className="card-body p-0">
            <div className="space-y-1">
              {stats.recentActivity.map((activity) => (
                <ActivityItem key={activity.id} activity={activity} />
              ))}
            </div>
          </div>
          <div className="card-footer">
            <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
              Ver toda la actividad
            </button>
          </div>
        </div>
      </div>

      {/* Performance Chart Placeholder */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-secondary-900">Rendimiento del Mes</h2>
          <p className="text-sm text-secondary-600">Archivos procesados por día</p>
        </div>
        <div className="card-body">
          <div className="h-64 flex items-center justify-center bg-secondary-50 rounded-lg">
            <div className="text-center">
              <BarChart3 className="w-16 h-16 text-secondary-400 mx-auto mb-4" />
              <p className="text-secondary-600">Gráfico de rendimiento próximamente</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
