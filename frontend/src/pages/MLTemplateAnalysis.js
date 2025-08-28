import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useAuth } from '../context/AuthContext';
import { fileService } from '../services/fileService';
import { logger } from '../utils/logger';
import { 
  Upload, 
  FileSpreadsheet, 
  File, 
  X, 
  Check, 
  AlertCircle,
  Loader,
  Download,
  Eye,
  FileText,
  Info,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { clsx } from 'clsx';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

const MLTemplateAnalysis = () => {
  const { user, isPremium } = useAuth();
  const [analysisFiles, setAnalysisFiles] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    for (const file of acceptedFiles) {
      // Validate file for ML template analysis
      const validation = fileService.validateMLTemplate(file);
      
      if (!validation.isValidMLTemplate) {
        toast.error(`${file.name}: ${validation.suggestedAction}`);
        continue;
      }

      // Validate file size (5MB for free, 50MB for premium)
      const maxSize = isPremium ? 50 * 1024 * 1024 : 5 * 1024 * 1024;
      if (file.size > maxSize) {
        toast.error(`${file.name}: Archivo muy grande. Máximo ${isPremium ? '50MB' : '5MB'}`);
        continue;
      }

      // Add file to analysis list
      const fileItem = {
        id: Date.now() + Math.random(),
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        status: 'analyzing',
        progress: 0,
        analysis: null,
        error: null,
      };

      setAnalysisFiles(prev => [...prev, fileItem]);

      try {
        setIsAnalyzing(true);
        
        // Analyze ML template
        const analysisResult = await fileService.analyzeMLTemplate(file, (progress) => {
          setAnalysisFiles(prev => 
            prev.map(f => 
              f.id === fileItem.id 
                ? { ...f, progress } 
                : f
            )
          );
        });

        // Update file with analysis results
        setAnalysisFiles(prev => 
          prev.map(f => 
            f.id === fileItem.id 
              ? { 
                  ...f, 
                  status: analysisResult.analysis.is_ml_template ? 'completed' : 'warning',
                  analysis: analysisResult,
                  progress: 100
                } 
              : f
          )
        );

        if (analysisResult.analysis.is_ml_template) {
          toast.success(`✅ ${file.name}: Plantilla ML detectada correctamente`);
        } else {
          toast.warning(`⚠️ ${file.name}: No parece ser una plantilla ML estándar`);
        }

      } catch (error) {
        logger.error('Analysis error:', error);
        setAnalysisFiles(prev => 
          prev.map(f => 
            f.id === fileItem.id 
              ? { 
                  ...f, 
                  status: 'error',
                  error: error.response?.data?.detail || error.message || 'Error de análisis',
                  progress: 100
                } 
              : f
          )
        );
        toast.error(`❌ Error analizando ${file.name}`);
      } finally {
        setIsAnalyzing(false);
      }
    }
  }, [isPremium]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv'],
    },
    maxFiles: isPremium ? 10 : 3,
    multiple: true,
  });

  const getFileIcon = (type) => {
    if (type.includes('spreadsheet') || type.includes('csv')) {
      return FileSpreadsheet;
    }
    return File;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const removeFile = (fileId) => {
    setAnalysisFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const viewAnalysis = (file) => {
    setSelectedAnalysis(file);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'analyzing':
        return <Loader className="w-4 h-4 animate-spin text-blue-500" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <File className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusText = (status, analysis) => {
    switch (status) {
      case 'analyzing':
        return 'Analizando...';
      case 'completed':
        return `✅ Plantilla ML válida (${analysis?.analysis?.total_products || 0} productos)`;
      case 'warning':
        return '⚠️ No es plantilla ML estándar';
      case 'error':
        return '❌ Error en análisis';
      default:
        return 'Pendiente';
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Análisis de Plantillas Mercado Libre
        </h1>
        <p className="text-gray-600">
          Sube tus archivos para verificar si siguen la estructura de plantilla ML estándar
        </p>
      </div>

      {/* Info Panel */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-start space-x-3">
          <Info className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h3 className="font-medium text-blue-900 mb-1">
              ¿Qué detectamos en las plantillas ML?
            </h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• <strong>Fila 4:</strong> Campos obligatorios marcados como "obligatorio"</li>
              <li>• <strong>Fila 5:</strong> Tipos de datos para cada columna</li>
              <li>• <strong>Fila 8+:</strong> Datos de productos</li>
              <li>• <strong>Columnas estándar:</strong> Título, precio, stock, categoría, etc.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* File Upload Area */}
      <div className="mb-6">
        <div
          {...getRootProps()}
          className={clsx(
            'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
            isDragActive
              ? 'border-blue-400 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          )}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-lg font-medium text-gray-900 mb-2">
            {isDragActive
              ? 'Suelta los archivos aquí...'
              : 'Arrastra archivos o haz clic para seleccionar'
            }
          </p>
          <p className="text-sm text-gray-500 mb-4">
            Archivos soportados: Excel (.xlsx, .xls) y CSV
          </p>
          <p className="text-xs text-gray-400">
            Máximo {isPremium ? '50MB por archivo, hasta 10 archivos' : '5MB por archivo, hasta 3 archivos'}
          </p>
        </div>
      </div>

      {/* Analysis Results */}
      {analysisFiles.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Resultados del Análisis
          </h2>

          {analysisFiles.map((file) => (
            <div key={file.id} className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  {getFileIcon(file.type) && 
                    React.createElement(getFileIcon(file.type), { 
                      className: "w-8 h-8 text-blue-600" 
                    })
                  }
                  <div>
                    <h3 className="font-medium text-gray-900">{file.name}</h3>
                    <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(file.status)}
                  <button
                    onClick={() => removeFile(file.id)}
                    className="text-gray-400 hover:text-red-500"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Progress Bar */}
              {file.status === 'analyzing' && (
                <div className="mb-3">
                  <div className="bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${file.progress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Status */}
              <div className="mb-3">
                <p className="text-sm font-medium">
                  {getStatusText(file.status, file.analysis)}
                </p>
                {file.error && (
                  <p className="text-sm text-red-600 mt-1">{file.error}</p>
                )}
              </div>

              {/* Analysis Details */}
              {file.analysis && (
                <div className="space-y-3">
                  {file.analysis.analysis.is_ml_template ? (
                    <div className="bg-green-50 border border-green-200 rounded p-3">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                        <div>
                          <span className="font-medium text-green-800">Productos:</span>
                          <p className="text-green-700">{file.analysis.analysis.total_products}</p>
                        </div>
                        <div>
                          <span className="font-medium text-green-800">Columnas obligatorias:</span>
                          <p className="text-green-700">
                            {Object.keys(file.analysis.analysis.template_structure?.obligatory_columns || {}).length}
                          </p>
                        </div>
                        <div>
                          <span className="font-medium text-green-800">Total columnas:</span>
                          <p className="text-green-700">
                            {Object.keys(file.analysis.analysis.detected_columns || {}).length}
                          </p>
                        </div>
                        <div>
                          <span className="font-medium text-green-800">Estado:</span>
                          <p className="text-green-700">
                            {file.analysis.analysis.validation_errors?.length === 0 ? 'Válida' : 'Con avisos'}
                          </p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                      <p className="text-sm text-yellow-800">
                        Este archivo no sigue la estructura estándar de plantilla ML
                      </p>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex space-x-2">
                    <button
                      onClick={() => viewAnalysis(file)}
                      className="flex items-center space-x-1 px-3 py-1.5 bg-blue-100 text-blue-700 rounded text-sm hover:bg-blue-200"
                    >
                      <Eye className="w-4 h-4" />
                      <span>Ver Detalles</span>
                    </button>
                    
                    {file.analysis?.file_saved && (
                      <>
                        <button
                          onClick={() => {
                            // Here you would navigate to mapping configuration
                            toast.success('Archivo guardado. Listo para mapeo!');
                          }}
                          className="flex items-center space-x-1 px-3 py-1.5 bg-green-100 text-green-700 rounded text-sm hover:bg-green-200"
                        >
                          <Check className="w-4 h-4" />
                          <span>Configurar Mapeo</span>
                        </button>
                        
                        {file.analysis?.mapping_patterns && (
                          <div className="text-xs text-purple-600 bg-purple-50 px-2 py-1 rounded">
                            🎯 Patrones generados ({(file.analysis.mapping_patterns.summary.confidence_score * 100).toFixed(0)}% confianza)
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Analysis Detail Modal */}
      {selectedAnalysis && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  Análisis Detallado: {selectedAnalysis.name}
                </h2>
                <button
                  onClick={() => setSelectedAnalysis(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {selectedAnalysis.analysis && (
                <div className="space-y-6">
                  {/* Template Structure */}
                  {selectedAnalysis.analysis.analysis.template_structure && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">Estructura de Plantilla</h3>
                      <div className="bg-gray-50 rounded p-4">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="font-medium">Fila de campos obligatorios:</span>
                            <p>Fila {selectedAnalysis.analysis.analysis.template_structure.obligatory_row}</p>
                          </div>
                          <div>
                            <span className="font-medium">Fila de tipos de datos:</span>
                            <p>Fila {selectedAnalysis.analysis.analysis.template_structure.data_type_row}</p>
                          </div>
                          <div>
                            <span className="font-medium">Inicio de datos:</span>
                            <p>Fila {selectedAnalysis.analysis.analysis.template_structure.data_start_row}</p>
                          </div>
                          <div>
                            <span className="font-medium">Total productos:</span>
                            <p>{selectedAnalysis.analysis.analysis.total_products}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Detected Columns */}
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">Columnas Detectadas</h3>
                    <div className="bg-gray-50 rounded p-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                        {Object.entries(selectedAnalysis.analysis.analysis.detected_columns || {}).map(([column, type]) => (
                          <div key={column} className="flex justify-between">
                            <span className="font-medium">{column}:</span>
                            <span className="text-gray-600">{type}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Validation Errors */}
                  {selectedAnalysis.analysis.analysis.validation_errors?.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-red-900 mb-3">Errores de Validación</h3>
                      <div className="bg-red-50 border border-red-200 rounded p-4">
                        <ul className="space-y-1 text-sm text-red-800">
                          {selectedAnalysis.analysis.analysis.validation_errors.map((error, index) => (
                            <li key={index}>• {error}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}

                  {/* Recommendations */}
                  {selectedAnalysis.analysis.analysis.recommendations?.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-blue-900 mb-3">Recomendaciones</h3>
                      <div className="bg-blue-50 border border-blue-200 rounded p-4">
                        <ul className="space-y-1 text-sm text-blue-800">
                          {selectedAnalysis.analysis.analysis.recommendations.map((rec, index) => (
                            <li key={index}>• {rec}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}

                  {/* Mapping Patterns */}
                  {selectedAnalysis.analysis.mapping_patterns && (
                    <div>
                      <h3 className="font-semibold text-purple-900 mb-3">
                        Patrones de Mapeo Generados
                        <span className="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                          Confianza: {(selectedAnalysis.analysis.mapping_patterns.summary.confidence_score * 100).toFixed(1)}%
                        </span>
                      </h3>
                      <div className="bg-purple-50 border border-purple-200 rounded p-4 space-y-4">
                        
                        {/* Mapping Summary */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                          <div>
                            <span className="font-medium text-purple-800">Campos mapeados:</span>
                            <p className="text-purple-700">
                              {selectedAnalysis.analysis.mapping_patterns.summary.mapped_fields} de {selectedAnalysis.analysis.mapping_patterns.summary.total_fields}
                            </p>
                          </div>
                          <div>
                            <span className="font-medium text-purple-800">Éxito de mapeo:</span>
                            <p className="text-purple-700">
                              {selectedAnalysis.analysis.mapping_patterns.summary.mapping_success_rate.toFixed(1)}%
                            </p>
                          </div>
                          <div>
                            <span className="font-medium text-purple-800">Alta confianza:</span>
                            <p className="text-purple-700">
                              {selectedAnalysis.analysis.mapping_patterns.summary.high_confidence_mappings} campos
                            </p>
                          </div>
                          <div>
                            <span className="font-medium text-purple-800">Revisión manual:</span>
                            <p className="text-purple-700">
                              {selectedAnalysis.analysis.mapping_patterns.summary.manual_review_needed} campos
                            </p>
                          </div>
                        </div>

                        {/* Field Mappings Table */}
                        <div>
                          <h4 className="font-medium text-purple-800 mb-2">Mapeo de Campos</h4>
                          <div className="overflow-x-auto">
                            <table className="min-w-full text-xs border border-purple-200">
                              <thead className="bg-purple-100">
                                <tr>
                                  <th className="px-2 py-1 text-left font-medium text-purple-800">Campo Origen</th>
                                  <th className="px-2 py-1 text-left font-medium text-purple-800">Campo ML</th>
                                  <th className="px-2 py-1 text-left font-medium text-purple-800">Confianza</th>
                                  <th className="px-2 py-1 text-left font-medium text-purple-800">Transformación</th>
                                  <th className="px-2 py-1 text-left font-medium text-purple-800">Ejemplos</th>
                                </tr>
                              </thead>
                              <tbody>
                                {selectedAnalysis.analysis.mapping_patterns.mapping_pattern.field_mappings.map((mapping, index) => (
                                  <tr key={index} className="border-t border-purple-200">
                                    <td className="px-2 py-1 font-medium">{mapping.source_column}</td>
                                    <td className="px-2 py-1">{mapping.target_field}</td>
                                    <td className="px-2 py-1">
                                      <span className={`px-1 py-0.5 rounded text-xs ${
                                        mapping.confidence === 'high' ? 'bg-green-100 text-green-800' :
                                        mapping.confidence === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                        'bg-red-100 text-red-800'
                                      }`}>
                                        {mapping.confidence}
                                      </span>
                                    </td>
                                    <td className="px-2 py-1">
                                      {mapping.transformation_rule ? (
                                        <span className="text-blue-600 text-xs">{mapping.transformation_rule}</span>
                                      ) : (
                                        <span className="text-gray-500 text-xs">Directo</span>
                                      )}
                                    </td>
                                    <td className="px-2 py-1 text-gray-600">
                                      {mapping.examples ? mapping.examples.slice(0, 2).join(', ') : '-'}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>

                        {/* Next Steps */}
                        {selectedAnalysis.analysis.mapping_patterns.next_steps && (
                          <div>
                            <h4 className="font-medium text-purple-800 mb-2">Próximos Pasos</h4>
                            <ul className="text-sm text-purple-700 space-y-1">
                              {selectedAnalysis.analysis.mapping_patterns.next_steps.map((step, index) => (
                                <li key={index}>• {step}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Sample Data */}
                  {selectedAnalysis.analysis.analysis.sample_data?.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">Vista Previa de Datos</h3>
                      <div className="bg-gray-50 rounded p-4 overflow-x-auto">
                        <table className="min-w-full text-sm">
                          <thead>
                            <tr>
                              {Object.keys(selectedAnalysis.analysis.analysis.sample_data[0] || {}).map(key => (
                                <th key={key} className="text-left p-2 font-medium border-b">
                                  {key}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {selectedAnalysis.analysis.analysis.sample_data.slice(0, 3).map((row, index) => (
                              <tr key={index}>
                                {Object.values(row).map((value, cellIndex) => (
                                  <td key={cellIndex} className="p-2 border-b text-gray-700">
                                    {String(value).substring(0, 50)}
                                    {String(value).length > 50 ? '...' : ''}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {isAnalyzing && (
        <div className="fixed inset-0 bg-black bg-opacity-25 flex items-center justify-center z-40">
          <div className="bg-white rounded-lg p-6 flex items-center space-x-3">
            <LoadingSpinner />
            <span className="text-gray-700">Analizando plantilla ML...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default MLTemplateAnalysis;
