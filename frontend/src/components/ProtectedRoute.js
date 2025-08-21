import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from './LoadingSpinner';

const ProtectedRoute = ({ children, requirePremium = false }) => {
  const { user, loading, isPremium } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" message="Verificando autenticación..." />
      </div>
    );
  }

  if (!user) {
    // Redirect to login page with return url
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requirePremium && !isPremium) {
    // Redirect to upgrade page or dashboard with message
    return <Navigate to="/dashboard" state={{ requirePremium: true }} replace />;
  }

  return children;
};

export default ProtectedRoute;
