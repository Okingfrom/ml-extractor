import api from './api';

export const authService = {
  // Login user
  async login(email, password) {
    try {
      console.log('🔐 Attempting login for:', email);
      const response = await api.post('/api/login', {
        email,
        password,
      });
      
      console.log('🔐 Login API response:', response);
      console.log('🔐 Login response data:', response.data);
      
      // Store token if provided
      if (response.data.token) {
        localStorage.setItem('token', response.data.token);
        console.log('🔐 Token stored:', response.data.token);
      }
      
      return response.data;
    } catch (error) {
      console.error('🔐 Login error:', error);
      throw error;
    }
  },

  // Register user
  async register(userData) {
    try {
      const response = await api.post('/api/register', userData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Logout user
  async logout() {
    try {
      await api.post('/api/logout');
      localStorage.removeItem('token');
    } catch (error) {
      // Even if logout fails, remove token
      localStorage.removeItem('token');
      throw error;
    }
  },

  // Verify account
  async verify(token) {
    try {
      const response = await api.post('/api/verify', { token });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get current user
  async getCurrentUser() {
    try {
      const response = await api.get('/api/user');
      return response.data.user;
    } catch (error) {
      throw error;
    }
  },

  // Update user profile
  async updateProfile(profileData) {
    try {
      const response = await api.put('/api/user/profile', profileData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Change password
  async changePassword(currentPassword, newPassword) {
    try {
      const response = await api.put('/api/user/password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Request password reset
  async requestPasswordReset(email) {
    try {
      const response = await api.post('/api/password-reset', { email });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Reset password
  async resetPassword(token, newPassword) {
    try {
      const response = await api.post('/api/password-reset/confirm', {
        token,
        password: newPassword,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};
