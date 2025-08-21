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

      const response = await api.post('/files/upload', formData, {
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

  // Analyze ML Template structure
  async analyzeMLTemplate(file, onProgress) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/files/analyze-ml-template', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress(percentCompleted);
          }
        },
      });

      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get ML analysis for a file
  async getMLAnalysis(fileId) {
    try {
      const response = await api.get(`/files/${fileId}/ml-analysis`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get file processing status
  async getProcessingStatus(taskId) {
    try {
      const response = await api.get(`/files/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get user files with pagination
  async getFiles(page = 1, size = 10) {
    try {
      const response = await api.get('/files', {
        params: { page, size }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get specific file details
  async getFile(fileId) {
    try {
      const response = await api.get(`/files/${fileId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Process file with mapping
  async processFile(fileId, processingRequest) {
    try {
      const response = await api.post(`/files/${fileId}/process`, processingRequest);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Download processed file
  async downloadFile(fileId) {
    try {
      const response = await api.get(`/files/${fileId}/download`, {
        responseType: 'blob',
      });

      // Extract filename from response headers if available
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'download';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

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

  // Delete uploaded file
  async deleteFile(fileId) {
    try {
      const response = await api.delete(`/files/${fileId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get user's upload history (alias for getFiles)
  async getUploadHistory(page = 1, limit = 20) {
    return this.getFiles(page, limit);
  },

  // Get processing tasks
  async getProcessingTasks(page = 1, size = 10) {
    try {
      const response = await api.get('/files/tasks', {
        params: { page, size }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // File validation utilities
  validateFile(file, maxSize = 5 * 1024 * 1024) { // 5MB default
    const errors = [];
    
    // Check file size
    if (file.size > maxSize) {
      errors.push(`El archivo es muy grande. Tamaño máximo: ${this.formatFileSize(maxSize)}`);
    }
    
    // Check file type for ML templates
    const allowedExtensions = ['.xlsx', '.xls', '.csv'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
      errors.push(`Tipo de archivo no soportado. Use: ${allowedExtensions.join(', ')}`);
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  },

  validateMLTemplate(file) {
    const allowedExtensions = ['.xlsx', '.xls', '.csv'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    return {
      isValidMLTemplate: allowedExtensions.includes(fileExtension),
      suggestedAction: allowedExtensions.includes(fileExtension) 
        ? 'Archivo válido para análisis ML' 
        : 'Use archivo Excel (.xlsx) o CSV para plantillas ML'
    };
  },

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  getFileIcon(filename) {
    const extension = filename.split('.').pop().toLowerCase();
    
    switch (extension) {
      case 'xlsx':
      case 'xls':
        return '📊';
      case 'csv':
        return '📋';
      case 'pdf':
        return '📄';
      case 'docx':
      case 'doc':
        return '📝';
      default:
        return '📁';
    }
  }
};
