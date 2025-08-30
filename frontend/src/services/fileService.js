import api from './api';
import { logger } from '../utils/logger';

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

  // Analyze Product Data for ML mapping
  async analyzeProductData(file, onProgress) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/api/files/analyze-product-data', formData, {
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
      logger.error('Product data analysis error:', error);
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
  

  // Analyze ML Template structure and fields
  async analyzeMLTemplate(file, onProgress) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/api/files/analyze-ml-template', formData, {
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

    // Generate ML file preview
  async generateMLFilePreview(mlTemplate, productData, mappingConfig, defaultSettings) {
    try {
      const formData = new FormData();
      formData.append('ml_template', mlTemplate);
      formData.append('product_data', productData);
      formData.append('mapping_config', JSON.stringify(mappingConfig));
      formData.append('default_settings', JSON.stringify(defaultSettings));

      const response = await api.post('/api/files/preview-ml-file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      logger.error('Error generating ML file preview:', error);
      throw error;
    }
  },

  // Generate ML file
  async generateMLFile(mlTemplateFile, productFile, mappingConfig, defaultSettings, onProgress, writeMode = 'fill-empty', edits = null) {
    try {
      const formData = new FormData();
      formData.append('ml_template', mlTemplateFile);
      formData.append('product_data', productFile);
      formData.append('mapping_config', JSON.stringify(mappingConfig));
      formData.append('default_settings', JSON.stringify(defaultSettings));
      // attach write_mode and optional edits JSON
      formData.append('write_mode', writeMode);
      if (edits) {
        formData.append('edits', JSON.stringify(edits));
      }

      const response = await api.post('/api/files/generate-ml-file', formData, {
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

  // Download generated ML file
  async downloadMLFile(filename) {
    try {
      const response = await api.get(`/api/files/download/${filename}`, {
        responseType: 'blob',
      });

      // Create blob URL for download
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      return { success: true, message: 'Descarga iniciada' };
    } catch (error) {
      throw error;
    }
  },

  // Generate final ML template with mappings (deprecated - use generateMLFile instead)
  async generateMLMapping(mlTemplateFile, productFile, mappingConfig, onProgress) {
    try {
      const formData = new FormData();
      formData.append('ml_template', mlTemplateFile);
      formData.append('product_file', productFile);
      formData.append('mapping_config', JSON.stringify(mappingConfig));

      const response = await api.post('/api/files/generate-ml-mapping', formData, {
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

  // Validate ML Template structure
  validateMLTemplateStructure(analysisResult) {
    if (!analysisResult?.analysis) {
      return {
        isValid: false,
        errors: ['No se pudo analizar la estructura del archivo'],
        suggestions: ['Verifica que sea una plantilla oficial de Mercado Libre']
      };
    }

    const analysis = analysisResult.analysis;
    const errors = [];
    const suggestions = [];

    // Check if it's recognized as ML template
    if (!analysis.is_ml_template) {
      errors.push('El archivo no parece ser una plantilla de Mercado Libre');
      suggestions.push('Descarga la plantilla oficial desde tu cuenta de ML');
    }

    // Check for required fields
    if (!analysis.ml_fields || analysis.ml_fields.length === 0) {
      errors.push('No se detectaron campos de ML en la plantilla');
      suggestions.push('Verifica que la plantilla no esté modificada');
    }

    // Check for categories
    if (!analysis.categories || analysis.categories.length === 0) {
      errors.push('No se detectaron categorías en la plantilla');
      suggestions.push('La plantilla debe tener categorías definidas');
    }

    return {
      isValid: errors.length === 0,
      errors,
      suggestions,
      fieldCount: analysis.ml_fields?.length || 0,
      categoryCount: analysis.categories?.length || 0
    };
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
