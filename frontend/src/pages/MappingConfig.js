import React, { useState, useEffect } from 'react';
import { mappingService } from '../services/mappingService';
import { logger } from '../utils/logger';
import { 
  Settings, 
  Plus, 
  Save, 
  Download, 
  Upload,
  ArrowRight,
  ArrowDown,
  Trash2,
  Copy,
  Wand2
} from 'lucide-react';
import { clsx } from 'clsx';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

const MappingConfig = () => {
  const [mappingConfig, setMappingConfig] = useState({
    columns: {},
    template_columns: [],
    mapping: {},
  });
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [previewData, setPreviewData] = useState([]);

  // ML-compatible fields
  const mlFields = [
    { key: 'title', label: 'Título del Producto', required: true, description: 'Nombre principal del producto' },
    { key: 'price', label: 'Precio', required: true, description: 'Precio de venta en números' },
    { key: 'description', label: 'Descripción', required: false, description: 'Descripción detallada del producto' },
    { key: 'category', label: 'Categoría', required: false, description: 'Categoría en Mercado Libre' },
    { key: 'brand', label: 'Marca', required: false, description: 'Marca del producto' },
    { key: 'model', label: 'Modelo', required: false, description: 'Modelo específico' },
    { key: 'condition', label: 'Condición', required: false, description: 'Nuevo, Usado, Reacondicionado' },
    { key: 'stock', label: 'Stock', required: false, description: 'Cantidad disponible' },
    { key: 'sku', label: 'SKU', required: false, description: 'Código único del producto' },
    { key: 'weight', label: 'Peso', required: false, description: 'Peso en gramos' },
    { key: 'dimensions', label: 'Dimensiones', required: false, description: 'Largo x Ancho x Alto' },
    { key: 'images', label: 'Imágenes', required: false, description: 'URLs de imágenes separadas por comas' },
  ];

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setIsLoading(true);
      
      const [configResult, templatesResult] = await Promise.all([
        mappingService.getMappingConfig(),
        mappingService.getMappingTemplates(),
      ]);

      if (configResult.success) {
        setMappingConfig(configResult.config);
      }

      if (templatesResult.success) {
        setTemplates(templatesResult.templates);
      }

      // Load sample data for preview
      setPreviewData([
        { 'Nombre Producto': 'iPhone 13 Pro', 'Precio': '999999', 'Descripción': 'Smartphone Apple con 128GB' },
        { 'Nombre Producto': 'Samsung Galaxy S21', 'Precio': '799999', 'Descripción': 'Android flagship con cámara de 108MP' },
        { 'Nombre Producto': 'MacBook Air M1', 'Precio': '1299999', 'Descripción': 'Laptop ultradelgada con chip M1' },
      ]);

    } catch (error) {
      logger.error('Error loading mapping data:', error);
      toast.error('Error cargando configuración de mapeo');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMappingChange = (sourceField, targetField) => {
    setMappingConfig(prev => ({
      ...prev,
      mapping: {
        ...prev.mapping,
        [sourceField]: targetField,
      },
    }));
  };

  const addCustomField = () => {
    const fieldName = prompt('Nombre del nuevo campo:');
    if (fieldName && !mappingConfig.template_columns.includes(fieldName)) {
      setMappingConfig(prev => ({
        ...prev,
        template_columns: [...prev.template_columns, fieldName],
      }));
    }
  };

  const removeCustomField = (fieldName) => {
    setMappingConfig(prev => ({
      ...prev,
      template_columns: prev.template_columns.filter(f => f !== fieldName),
      mapping: Object.fromEntries(
        Object.entries(prev.mapping).filter(([, target]) => target !== fieldName)
      ),
    }));
  };

  const saveMapping = async () => {
    try {
      setIsSaving(true);
      // Transform mapping from { sourceField: mlKey } to { ML Label: sourceField }
      const backendMapping = {};
      Object.entries(mappingConfig.mapping).forEach(([source, targetKey]) => {
        if (!targetKey) return;
        const ml = mlFields.find(f => f.key === targetKey);
        const mlLabel = ml ? ml.label : targetKey;
        backendMapping[mlLabel] = source;
      });

      const payload = {
        ...mappingConfig,
        mapping: backendMapping,
      };

      const result = await mappingService.saveMappingConfig(payload);
      
      if (result.success) {
        toast.success('Configuración guardada exitosamente');
      } else {
        toast.error(result.error || 'Error guardando configuración');
      }
    } catch (error) {
      logger.error('Error saving mapping:', error);
      toast.error('Error guardando configuración');
    } finally {
      setIsSaving(false);
    }
  };

  const exportMappingJSON = () => {
    // Build backend-shaped mapping and trigger download
    const backendMapping = {};
    Object.entries(mappingConfig.mapping).forEach(([source, targetKey]) => {
      if (!targetKey) return;
      const ml = mlFields.find(f => f.key === targetKey);
      const mlLabel = ml ? ml.label : targetKey;
      backendMapping[mlLabel] = source;
    });

    const exportObj = {
      template_columns: mappingConfig.template_columns,
      mapping: backendMapping,
      exported_at: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(exportObj, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mapping_export.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const loadTemplate = async (templateId) => {
    if (!templateId) return;
    
    try {
      const template = templates.find(t => t.id === templateId);
      if (template) {
        setMappingConfig(template.config);
        toast.success(`Plantilla "${template.name}" cargada`);
      }
    } catch (error) {
      toast.error('Error cargando plantilla');
    }
  };

  const getSourceFields = () => {
    // Get source fields from preview data
    if (previewData.length > 0) {
      return Object.keys(previewData[0]);
    }
    return ['Nombre Producto', 'Precio', 'Descripción', 'Categoría', 'Stock', 'SKU'];
  };

  const MappingRow = ({ sourceField, targetField, onMappingChange }) => (
    <div className="flex items-center space-x-4 p-4 bg-secondary-50 rounded-lg">
      {/* Source Field */}
      <div className="flex-1">
        <div className="font-medium text-secondary-900">{sourceField}</div>
        <div className="text-sm text-secondary-600">Campo en tu archivo</div>
      </div>

      {/* Arrow */}
      <ArrowRight className="w-5 h-5 text-secondary-400" />

      {/* Target Field Selector */}
      <div className="flex-1">
        <select
          value={targetField || ''}
          onChange={(e) => onMappingChange(sourceField, e.target.value)}
          className="w-full input-field"
        >
          <option value="">Sin mapear</option>
          {mlFields.map((field) => (
            <option key={field.key} value={field.key}>
              {field.label} {field.required && '*'}
            </option>
          ))}
        </select>
        {targetField && (
          <div className="text-sm text-secondary-600 mt-1">
            {mlFields.find(f => f.key === targetField)?.description}
          </div>
        )}
      </div>

      {/* Preview */}
      <div className="flex-1">
        <div className="text-sm font-mono bg-white p-2 rounded border">
          {previewData.length > 0 ? previewData[0][sourceField] || 'N/A' : 'Vista previa'}
        </div>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="large" message="Cargando configuración de mapeo..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-secondary-900">
              Configuración de Mapeo
            </h1>
            <p className="text-secondary-600 mt-1">
              Define cómo mapear los campos de tus archivos a los campos de Mercado Libre
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={saveMapping}
              disabled={isSaving}
              className="btn-primary flex items-center space-x-2"
            >
              {isSaving ? (
                <LoadingSpinner size="small" color="white" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              <span>Guardar</span>
            </button>
          </div>
        </div>
      </div>

      {/* Templates Section */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-secondary-900">Plantillas</h2>
          <p className="text-sm text-secondary-600">
            Usa plantillas predefinidas o crea la tuya propia
          </p>
        </div>
        
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Cargar Plantilla
              </label>
              <select
                value={selectedTemplate}
                onChange={(e) => {
                  setSelectedTemplate(e.target.value);
                  loadTemplate(e.target.value);
                }}
                className="w-full input-field"
              >
                <option value="">Seleccionar plantilla...</option>
                {templates.map((template) => (
                  <option key={template.id} value={template.id}>
                    {template.name}
                  </option>
                ))}
              </select>
            </div>

            <button className="btn-secondary flex items-center justify-center space-x-2 h-fit self-end">
              <Plus className="w-4 h-4" />
              <span>Nueva Plantilla</span>
            </button>

            <button className="btn-secondary flex items-center justify-center space-x-2 h-fit self-end">
              <Wand2 className="w-4 h-4" />
              <span>Auto-detectar</span>
            </button>
          </div>
        </div>
      </div>

      {/* Field Mapping */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-secondary-900">Mapeo de Campos</h2>
          <p className="text-sm text-secondary-600">
            Relaciona los campos de tu archivo con los campos de Mercado Libre
          </p>
        </div>
        
        <div className="card-body">
          {/* Header Row */}
          <div className="grid grid-cols-3 gap-4 p-4 bg-secondary-100 rounded-lg mb-4">
            <div className="font-semibold text-secondary-900">Campo Original</div>
            <div className="font-semibold text-secondary-900">Campo ML</div>
            <div className="font-semibold text-secondary-900">Vista Previa</div>
          </div>

          {/* Mapping Rows */}
          <div className="space-y-3">
            {getSourceFields().map((sourceField) => (
              <MappingRow
                key={sourceField}
                sourceField={sourceField}
                targetField={mappingConfig.mapping[sourceField]}
                onMappingChange={handleMappingChange}
              />
            ))}
          </div>

          {/* Add Custom Field */}
          <div className="mt-6 pt-4 border-t border-secondary-200">
            <button
              onClick={addCustomField}
              className="btn-secondary flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Agregar Campo Personalizado</span>
            </button>
          </div>
        </div>
      </div>

      {/* Required Fields Check */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-secondary-900">Validación de Campos</h2>
        </div>
        
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Required Fields */}
            <div>
              <h3 className="font-medium text-secondary-900 mb-3">Campos Requeridos</h3>
              <div className="space-y-2">
                {mlFields.filter(field => field.required).map((field) => {
                  const isMapped = Object.values(mappingConfig.mapping).includes(field.key);
                  return (
                    <div
                      key={field.key}
                      className={clsx(
                        'flex items-center space-x-3 p-3 rounded-lg',
                        isMapped ? 'bg-success-50 border border-success-200' : 'bg-error-50 border border-error-200'
                      )}
                    >
                      <div className={clsx(
                        'w-2 h-2 rounded-full',
                        isMapped ? 'bg-success-500' : 'bg-error-500'
                      )} />
                      <div>
                        <div className="font-medium text-secondary-900">{field.label}</div>
                        <div className="text-sm text-secondary-600">{field.description}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Optional Fields */}
            <div>
              <h3 className="font-medium text-secondary-900 mb-3">Campos Opcionales Mapeados</h3>
              <div className="space-y-2">
                {mlFields.filter(field => !field.required && Object.values(mappingConfig.mapping).includes(field.key)).map((field) => (
                  <div
                    key={field.key}
                    className="flex items-center space-x-3 p-3 rounded-lg bg-blue-50 border border-blue-200"
                  >
                    <div className="w-2 h-2 rounded-full bg-blue-500" />
                    <div>
                      <div className="font-medium text-secondary-900">{field.label}</div>
                      <div className="text-sm text-secondary-600">{field.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Export/Import */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-secondary-900">Exportar/Importar Configuración</h2>
        </div>
        
        <div className="card-body">
          <div className="flex items-center space-x-4">
            <button onClick={exportMappingJSON} className="btn-secondary flex items-center space-x-2">
              <Download className="w-4 h-4" />
              <span>Exportar JSON</span>
            </button>
            
            <button className="btn-secondary flex items-center space-x-2">
              <Upload className="w-4 h-4" />
              <span>Importar JSON</span>
            </button>
            
            <button className="btn-secondary flex items-center space-x-2">
              <Copy className="w-4 h-4" />
              <span>Copiar como Plantilla</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MappingConfig;
