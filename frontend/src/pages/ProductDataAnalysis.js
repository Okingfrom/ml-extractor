import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useAuth } from '../context/AuthContext';
import { fileService } from '../services/fileService';
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
  XCircle,
  Package,
  ShoppingCart,
  Target,
  Zap,
  BarChart3
} from 'lucide-react';
import { clsx } from 'clsx';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

const ProductDataAnalysis = () => {
  const { user, isPremium } = useAuth();
  const [analysisFiles, setAnalysisFiles] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [activeTab, setActiveTab] = useState('product-analysis'); // 'product-analysis' or 'ml-template'

  const onDrop = useCallback(async (acceptedFiles) => {
    if (!user) {
      toast.error('Debes estar logueado para usar esta función');
      return;
    }

    if (activeTab === 'product-analysis') {
      // Product Data Analysis Logic
      const file = acceptedFiles[0];
      if (!file) return;

      const allowedTypes = [
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv'
      ];

      if (!allowedTypes.includes(file.type)) {
        toast.error('Solo se permiten archivos Excel (.xlsx, .xls) o CSV');
        return;
      }

      if (file.size > 50 * 1024 * 1024) { // 50MB
        toast.error('El archivo es demasiado grande. Máximo 50MB');
        return;
      }

      setIsAnalyzing(true);
      
      try {
        console.log('🔍 Iniciando análisis de productos...');
        
        // Call the new product data analysis endpoint
        const analysisResult = await fileService.analyzeProductData(file);
        
        console.log('✅ Análisis completado:', analysisResult);
        
        const analysisItem = {
          id: Date.now(),
          fileName: file.name,
          fileSize: file.size,
          uploadTime: new Date().toISOString(),
          status: 'completed',
          analysis: analysisResult,
          analysisType: 'product-analysis'
        };

        setAnalysisFiles(prev => [analysisItem, ...prev]);
        setSelectedAnalysis(analysisItem);
        
        toast.success(`✅ Análisis completado: ${analysisResult.file_analysis?.total_products || 0} productos detectados`);
        
      } catch (error) {
        console.error('❌ Error en análisis:', error);
        
        const errorAnalysis = {
          id: Date.now(),
          fileName: file.name,
          fileSize: file.size,
          uploadTime: new Date().toISOString(),
          status: 'error',
          error: error.message || 'Error desconocido',
          analysisType: 'product-analysis'
        };

        setAnalysisFiles(prev => [errorAnalysis, ...prev]);
        toast.error(`❌ Error: ${error.message || 'No se pudo analizar el archivo'}`);
        
      } finally {
        setIsAnalyzing(false);
      }

    } else if (activeTab === 'ml-template') {
      // ML Template Analysis Logic
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
          fileName: file.name,
          fileSize: file.size,
          uploadTime: new Date().toISOString(),
          status: 'analyzing',
          progress: 0,
          analysis: null,
          error: null,
          analysisType: 'ml-template'
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
          console.error('Analysis error:', error);
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
    }
  }, [user, isPremium, activeTab]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv']
    },
    multiple: activeTab === 'ml-template' ? (isPremium ? 10 : 3) : false,
    disabled: isAnalyzing
  });

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type) => {
    if (type?.includes('spreadsheet') || type?.includes('csv')) {
      return FileSpreadsheet;
    }
    return File;
  };

  const removeFile = (fileId) => {
    setAnalysisFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const viewAnalysis = (file) => {
    setSelectedAnalysis(file);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Loader className="w-5 h-5 text-blue-500 animate-spin" />;
    }
  };

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getMappingStatusColor = (status) => {
    switch (status) {
      case 'high_confidence':
        return 'bg-green-100 text-green-800';
      case 'medium_confidence':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-red-100 text-red-800';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Package className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analizador de Productos y ML</h1>
            <p className="text-gray-600">Analiza tus archivos de productos y plantillas ML para obtener mapeos automáticos</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('product-analysis')}
              className={clsx(
                'py-4 px-1 border-b-2 font-medium text-sm',
                activeTab === 'product-analysis'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              )}
            >
              <div className="flex items-center space-x-2">
                <ShoppingCart className="w-5 h-5" />
                <span>Análisis de Productos</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('ml-template')}
              className={clsx(
                'py-4 px-1 border-b-2 font-medium text-sm',
                activeTab === 'ml-template'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              )}
            >
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5" />
                <span>Análisis ML Template</span>
              </div>
            </button>
          </nav>
        </div>

        {/* Info Cards */}
        <div className="grid md:grid-cols-3 gap-4 mb-6">
          {activeTab === 'product-analysis' ? (
            <>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="flex items-center space-x-2 mb-2">
                  <FileSpreadsheet className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-blue-900">Análisis Automático</h3>
                </div>
                <p className="text-sm text-blue-700">Detecta automáticamente campos como título, precio, stock, categoría, etc.</p>
              </div>

              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <div className="flex items-center space-x-2 mb-2">
                  <Target className="w-5 h-5 text-green-600" />
                  <h3 className="font-semibold text-green-900">Mapeo Inteligente</h3>
                </div>
                <p className="text-sm text-green-700">Sugiere automáticamente cómo mapear tus campos a la plantilla de ML</p>
              </div>

              <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                <div className="flex items-center space-x-2 mb-2">
                  <ShoppingCart className="w-5 h-5 text-purple-600" />
                  <h3 className="font-semibold text-purple-900">Productos Detectados</h3>
                </div>
                <p className="text-sm text-purple-700">Identifica cantidad de productos y estructura de datos</p>
              </div>
            </>
          ) : (
            <>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="flex items-center space-x-2 mb-2">
                  <Zap className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-blue-900">Validación ML</h3>
                </div>
                <p className="text-sm text-blue-700">Verifica si el archivo es una plantilla válida de Mercado Libre</p>
              </div>

              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <div className="flex items-center space-x-2 mb-2">
                  <BarChart3 className="w-5 h-5 text-green-600" />
                  <h3 className="font-semibold text-green-900">Estructura</h3>
                </div>
                <p className="text-sm text-green-700">Analiza estructura de campos y formato de la plantilla</p>
              </div>

              <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                <div className="flex items-center space-x-2 mb-2">
                  <FileText className="w-5 h-5 text-purple-600" />
                  <h3 className="font-semibold text-purple-900">Compatibilidad</h3>
                </div>
                <p className="text-sm text-purple-700">Verifica compatibilidad con el formato estándar de ML</p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Upload Area */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div 
          {...getRootProps()} 
          className={clsx(
            "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
            isDragActive ? "border-blue-400 bg-blue-50" : "border-gray-300 hover:border-gray-400",
            isAnalyzing && "opacity-50 cursor-not-allowed"
          )}
        >
          <input {...getInputProps()} />
          
          {isAnalyzing ? (
            <div className="space-y-4">
              <Loader className="w-12 h-12 text-blue-500 animate-spin mx-auto" />
              <div>
                <p className="text-lg font-medium text-gray-900">Analizando productos...</p>
                <p className="text-gray-600">Esto puede tomar unos momentos</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <Upload className="w-12 h-12 text-gray-400 mx-auto" />
              <div>
                <p className="text-lg font-medium text-gray-900">
                  {isDragActive ? 'Suelta tu archivo aquí' : 'Sube tu archivo de productos'}
                </p>
                <p className="text-gray-600">Excel (.xlsx, .xls) o CSV hasta 50MB</p>
              </div>
              <button
                type="button"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Seleccionar archivo
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Analysis History */}
      {analysisFiles.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Historial de Análisis</h2>
          
          <div className="space-y-3">
            {analysisFiles.map((analysis) => (
              <div
                key={analysis.id}
                className={clsx(
                  "p-4 rounded-lg border cursor-pointer transition-colors",
                  selectedAnalysis?.id === analysis.id 
                    ? "border-blue-500 bg-blue-50" 
                    : "border-gray-200 hover:border-gray-300"
                )}
                onClick={() => setSelectedAnalysis(analysis)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(analysis.status)}
                    <div>
                      <p className="font-medium text-gray-900">{analysis.fileName}</p>
                      <p className="text-sm text-gray-600">
                        {formatFileSize(analysis.fileSize)} • {new Date(analysis.uploadTime).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  
                  {analysis.status === 'completed' && analysis.analysis && (
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        {analysis.analysis.file_analysis?.total_products || 0} productos
                      </p>
                      <p className="text-xs text-gray-600">
                        {analysis.analysis.ml_template_mapping?.mapping_summary?.mapped_fields || 0} campos mapeados
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {selectedAnalysis && selectedAnalysis.status === 'completed' && selectedAnalysis.analysis && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Resultados del Análisis</h2>
          
          {/* Summary Stats */}
          <div className="grid md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-blue-600 font-medium">Total Productos</p>
              <p className="text-2xl font-bold text-blue-900">
                {selectedAnalysis.analysis.file_analysis?.total_products || 0}
              </p>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-sm text-green-600 font-medium">Campos Detectados</p>
              <p className="text-2xl font-bold text-green-900">
                {selectedAnalysis.analysis.file_analysis?.column_count || 0}
              </p>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-sm text-purple-600 font-medium">Campos Mapeados</p>
              <p className="text-2xl font-bold text-purple-900">
                {selectedAnalysis.analysis.ml_template_mapping?.mapping_summary?.mapped_fields || 0}
              </p>
            </div>
            
            <div className="bg-yellow-50 p-4 rounded-lg">
              <p className="text-sm text-yellow-600 font-medium">Confianza</p>
              <p className={clsx(
                "text-2xl font-bold",
                getConfidenceColor(selectedAnalysis.analysis.ml_template_mapping?.mapping_summary?.overall_confidence_score || 0).split(' ')[0]
              )}>
                {Math.round((selectedAnalysis.analysis.ml_template_mapping?.mapping_summary?.overall_confidence_score || 0) * 100)}%
              </p>
            </div>
          </div>

          {/* Field Mappings */}
          {selectedAnalysis.analysis.ml_template_mapping?.field_mappings && (
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Mapeo de Campos</h3>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Campo Origen
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Campo ML Destino
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Confianza
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Requerido
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Ejemplos
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {selectedAnalysis.analysis.ml_template_mapping.field_mappings.map((mapping, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {mapping.source_column}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {mapping.target_ml_field || 'Sin mapear'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={clsx(
                            "inline-flex px-2 py-1 text-xs font-semibold rounded-full",
                            getMappingStatusColor(mapping.status || mapping.confidence)
                          )}>
                            {mapping.status === 'high_confidence' || mapping.confidence === 'high' ? 'Alta' :
                             mapping.status === 'medium_confidence' || mapping.confidence === 'medium' ? 'Media' : 'Baja'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {mapping.ml_field_required ? 
                            <Check className="w-4 h-4 text-green-500" /> : 
                            <X className="w-4 h-4 text-gray-400" />
                          }
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                          {mapping.examples?.slice(0, 2).join(', ') || 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Recommendations */}
          {selectedAnalysis.analysis.recommendations && (
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recomendaciones</h3>
              
              <div className="space-y-2">
                {selectedAnalysis.analysis.recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-gray-700">{recommendation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              <Download className="w-4 h-4 mr-2" />
              Generar Plantilla ML
            </button>
            
            <button className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              <Eye className="w-4 h-4 mr-2" />
              Vista Previa
            </button>
          </div>
        </div>
      )}

      {/* Error Display */}
      {selectedAnalysis && selectedAnalysis.status === 'error' && (
        <div className="bg-white rounded-lg shadow-sm border border-red-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <AlertCircle className="w-6 h-6 text-red-500" />
            <h2 className="text-lg font-semibold text-red-900">Error en el Análisis</h2>
          </div>
          
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-700">{selectedAnalysis.error}</p>
          </div>
          
          <div className="mt-4">
            <h3 className="font-medium text-gray-900 mb-2">Posibles soluciones:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Verifica que el archivo no esté corrupto</li>
              <li>• Asegúrate de que tenga datos en las primeras filas</li>
              <li>• Revisa que el formato sea Excel (.xlsx, .xls) o CSV</li>
              <li>• Intenta con un archivo más pequeño si es muy grande</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDataAnalysis;
