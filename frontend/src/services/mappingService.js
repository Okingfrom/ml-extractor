import api from './api';

export const mappingService = {
  // Get mapping configuration
  async getMappingConfig() {
    try {
      const response = await api.get('/api/mapping/config');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Save mapping configuration
  async saveMappingConfig(config) {
    try {
      const response = await api.post('/api/mapping/config', config);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get available mapping templates
  async getMappingTemplates() {
    try {
      const response = await api.get('/api/mapping/templates');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Create new mapping template
  async createMappingTemplate(template) {
    try {
      const response = await api.post('/api/mapping/templates', template);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update mapping template
  async updateMappingTemplate(templateId, template) {
    try {
      const response = await api.put(`/api/mapping/templates/${templateId}`, template);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Delete mapping template
  async deleteMappingTemplate(templateId) {
    try {
      const response = await api.delete(`/api/mapping/templates/${templateId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Apply mapping to data
  async applyMapping(dataId, mappingConfig) {
    try {
      const response = await api.post('/api/mapping/apply', {
        data_id: dataId,
        mapping: mappingConfig,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get ML-compatible field mappings
  async getMLFieldMappings() {
    try {
      const response = await api.get('/api/mapping/ml-fields');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Validate mapping configuration
  async validateMapping(config) {
    try {
      const response = await api.post('/api/mapping/validate', config);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Auto-detect mapping suggestions
  async getAutoMappingSuggestions(dataPreview) {
    try {
      const response = await api.post('/api/mapping/auto-detect', {
        data: dataPreview,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};
