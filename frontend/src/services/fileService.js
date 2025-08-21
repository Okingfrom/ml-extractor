import api from './api';

export const fileService = {
  // Upload file for processing
  async uploadFile(file, options = {}) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Add additional options
      Object.keys(options).forEach(key => {
        formData.append(key, options[key]);
      });

      const response = await api.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (options.onProgress) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            options.onProgress(percentCompleted);
          }
        },
      });

      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get file processing status
  async getProcessingStatus(taskId) {
    try {
      const response = await api.get(`/api/processing/${taskId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Download processed file
  async downloadFile(taskId, filename) {
    try {
      const response = await api.get(`/api/download/${taskId}`, {
        responseType: 'blob',
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      return true;
    } catch (error) {
      throw error;
    }
  },

  // Get supported file types
  async getSupportedTypes() {
    try {
      const response = await api.get('/api/file-types');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Delete uploaded file
  async deleteFile(taskId) {
    try {
      const response = await api.delete(`/api/files/${taskId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get user's upload history
  async getUploadHistory(page = 1, limit = 20) {
    try {
      const response = await api.get('/api/uploads', {
        params: { page, limit },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};
