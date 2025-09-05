import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Pages
import Login from './pages/LoginSimple';
import Register from './pages/Register';
import Dashboard from './pages/DashboardSimple';
import FileUpload from './pages/FileUpload';
import ProductDataAnalysis from './pages/ProductDataAnalysis';
import MLMappingWizard from './pages/MLMappingWizard';
import MappingConfig from './pages/MappingConfig';
import AdminSettings from './pages/AdminSettings';

// Components
import Layout from './components/Layout';
import LoadingSpinner from './components/LoadingSpinner';
import ProtectedRoute from './components/ProtectedRoute';
import DebugPanel from './components/DebugPanel';

function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="App">
  {process.env.NODE_ENV === 'development' && <DebugPanel />}
      <Routes>
        {/* Public Routes */}
        <Route 
          path="/login" 
          element={user ? <Navigate to="/dashboard" replace /> : <Login />} 
        />
        <Route 
          path="/register" 
          element={user ? <Navigate to="/dashboard" replace /> : <Register />} 
        />
        
        {/* Protected Routes */}
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="upload" element={<FileUpload />} />
          <Route path="product-analysis" element={<ProductDataAnalysis />} />
          <Route path="ml-mapping" element={<MLMappingWizard />} />
          <Route path="mapping" element={<MappingConfig />} />
          <Route path="admin/settings" element={<AdminSettings />} />
        </Route>
        
        {/* Catch all route */}
        <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} replace />} />
      </Routes>
    </div>
  );
}

export default App;
