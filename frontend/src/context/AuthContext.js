import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';
import toast from 'react-hot-toast';

const AuthContext = createContext({});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (error) {
      // User not authenticated
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setLoading(true);
      const response = await authService.login(email, password);
      
      if (response.success) {
        setUser(response.user);
        toast.success(`¡Bienvenido ${response.user.first_name}!`);
        return { success: true };
      } else {
        toast.error(response.error || 'Error al iniciar sesión');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Error de conexión';
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      const response = await authService.register(userData);
      
      if (response.success) {
        toast.success('Registro exitoso. Revisa tu email para verificar tu cuenta.');
        return { success: true };
      } else {
        toast.error(response.error || 'Error en el registro');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Error de conexión';
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
      setUser(null);
      toast.success('Sesión cerrada correctamente');
    } catch (error) {
      console.error('Error during logout:', error);
      // Even if logout fails, clear local state
      setUser(null);
    }
  };

  const verifyAccount = async (token) => {
    try {
      const response = await authService.verify(token);
      
      if (response.success) {
        toast.success('Cuenta verificada exitosamente');
        return { success: true };
      } else {
        toast.error(response.error || 'Error en la verificación');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Error de conexión';
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await authService.updateProfile(profileData);
      
      if (response.success) {
        setUser(response.user);
        toast.success('Perfil actualizado correctamente');
        return { success: true };
      } else {
        toast.error(response.error || 'Error al actualizar perfil');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Error de conexión';
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    verifyAccount,
    updateProfile,
    checkAuthStatus,
    isAuthenticated: !!user,
    isPremium: user?.account_type === 'premium',
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
