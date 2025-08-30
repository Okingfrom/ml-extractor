import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, 
  FileText, 
  CheckCircle,
  Crown,
  ArrowRight
} from 'lucide-react';

const DashboardSimple = () => {
  const { user, isPremium } = useAuth();
  const navigate = useNavigate();

  const quickActions = [
    {
      title: "Subir Productos",
      description: "Sube tu archivo Excel o CSV con productos",
      icon: Upload,
      action: () => navigate('/upload'),
      color: "bg-blue-500"
    },
    {
      title: "Ver Resultados",
      description: "Descarga tu archivo listo para Mercado Libre",
      icon: FileText,
      action: () => navigate('/results'),
      color: "bg-green-500"
    },
    {
      title: "Configurar Campos",
      description: "Personaliza cómo se convierten tus datos",
      icon: CheckCircle,
      action: () => navigate('/mapping'),
      color: "bg-purple-500",
      premium: true
    }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Simple Welcome */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">
          ¡Hola, {user?.first_name}! 👋
        </h1>
        <p className="text-xl text-gray-600">
          Convierte tus productos para Mercado Libre en 3 pasos simples
        </p>
        
        {!isPremium && (
          <div className="inline-flex items-center space-x-2 bg-yellow-100 text-yellow-800 px-4 py-2 rounded-full text-sm">
            <span>Plan Gratuito</span>
            <Crown className="w-4 h-4" />
            <button className="text-yellow-900 underline hover:no-underline">
              Actualizar
            </button>
          </div>
        )}
      </div>

      {/* Simple Process Steps */}
      <div className="grid md:grid-cols-3 gap-6">
        {quickActions.map((action, index) => {
          const Icon = action.icon;
          const isDisabled = action.premium && !isPremium;
          
          return (
            <button
              key={action.title}
              onClick={isDisabled ? undefined : action.action}
              className={`
                relative p-6 rounded-xl border-2 border-dashed transition-all duration-200 text-left
                ${isDisabled 
                  ? 'border-gray-200 bg-gray-50 cursor-not-allowed opacity-60' 
                  : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50 cursor-pointer'
                }
              `}
            >
              {/* Step Number */}
              <div className="absolute -top-3 -left-3 w-8 h-8 bg-white border-2 border-gray-300 rounded-full flex items-center justify-center text-sm font-bold text-gray-600">
                {index + 1}
              </div>
              
              {/* Premium Badge */}
              {action.premium && (
                <div className="absolute top-3 right-3">
                  <Crown className="w-5 h-5 text-yellow-600" />
                </div>
              )}

              <div className="space-y-4">
                <div className={`w-12 h-12 ${action.color} rounded-lg flex items-center justify-center`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {action.title}
                  </h3>
                  <p className="text-gray-600 text-sm">
                    {action.description}
                  </p>
                </div>
                
                {!isDisabled && (
                  <div className="flex items-center text-blue-600 text-sm font-medium">
                    Comenzar
                    <ArrowRight className="w-4 h-4 ml-1" />
                  </div>
                )}
                
                {isDisabled && (
                  <div className="text-gray-400 text-sm font-medium">
                    Requiere plan Premium
                  </div>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Simple Help Section */}
      <div className="bg-blue-50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          ¿Cómo funciona?
        </h3>
        <div className="text-gray-700 space-y-2 text-sm">
          <p>1. <strong>Sube tu archivo:</strong> Excel o CSV con tus productos</p>
          <p>2. <strong>Revisamos automáticamente:</strong> Convertimos tus datos al formato de Mercado Libre</p>
          <p>3. <strong>Descarga el resultado:</strong> Archivo listo para subir a tu tienda</p>
        </div>
      </div>
    </div>
  );
};

export default DashboardSimple;
