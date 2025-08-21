import React from 'react';

const DataValidation = () => {
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <h1 className="text-2xl font-bold text-secondary-900">Validación de Datos</h1>
        <p className="text-secondary-600 mt-1">
          Revisa y valida tus datos antes de exportar a Mercado Libre
        </p>
        
        <div className="mt-8 flex items-center justify-center h-64 bg-secondary-50 rounded-lg">
          <div className="text-center">
            <div className="text-4xl mb-4">🚧</div>
            <h3 className="text-lg font-medium text-secondary-900 mb-2">
              Validación de Datos
            </h3>
            <p className="text-secondary-600">
              Esta funcionalidad está en desarrollo
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataValidation;
