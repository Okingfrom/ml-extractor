import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { useAuth } from '../context/AuthContext';
import { fileService } from '../services/fileService';
import { logger } from '../utils/logger';
import { mapHeaderToLogical } from '../utils/headerMapper';
import MLFilePreview from '../components/MLFilePreview';
import { 
  FileSpreadsheet, 
  X, 
  Check, 
  AlertCircle,
  Loader,
  Download,
  CheckCircle,
  XCircle,
  Package,
  Target,
  List,
  Settings,
  ArrowRight,
  ArrowLeft,
  Star,
  RefreshCw,
  Upload
} from 'lucide-react';
import { clsx } from 'clsx';
import toast from 'react-hot-toast';

const MLMappingWizard = () => {
  const { user } = useAuth();
  
  // Wizard State
  const [currentStep, setCurrentStep] = useState(1);
  const [wizardData, setWizardData] = useState({
    mlTemplate: null,
    mlTemplateAnalysis: null,
    selectedCategory: null,
    defaultSettings: {},
    productFile: null,
    productAnalysis: null,
    fieldMappings: {},
    finalMapping: null
  });
  
  // UI State
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const steps = [
    { id: 1, title: 'Plantilla ML', description: 'Sube tu plantilla de Mercado Libre', icon: FileSpreadsheet },
    { id: 2, title: 'Validación', description: 'Verificamos la plantilla', icon: CheckCircle },
    { id: 3, title: 'Categoría', description: 'Selecciona la categoría a llenar', icon: List },
    { id: 4, title: 'Configuración', description: 'Define valores por defecto', icon: Settings },
    { id: 5, title: 'Productos', description: 'Sube tu archivo de productos', icon: Package },
    { id: 6, title: 'Mapeo', description: 'Selecciona campos a mapear', icon: Target },
    { id: 7, title: 'Resultado', description: 'Revisa y descarga', icon: Download }
  ];

  // Step 1: Upload ML Template
  const handleMLTemplateUpload = useCallback(async (acceptedFiles) => {
    if (!acceptedFiles.length) return;
    
    const file = acceptedFiles[0];
    setIsLoading(true);
    setError(null);

    try {
      logger.info('🔍 Analizando plantilla ML...');
      
      // Validate ML template first
      const validation = fileService.validateMLTemplate(file);
      if (!validation.isValidMLTemplate) {
        throw new Error(validation.suggestedAction);
      }

      // Analyze ML template structure
      const analysisResult = await fileService.analyzeMLTemplate(file);
      
      logger.info('✅ Análisis de plantilla completado:', analysisResult);
      
      setWizardData(prev => ({
        ...prev,
        mlTemplate: file,
        mlTemplateAnalysis: analysisResult
      }));
      
      toast.success('✅ Plantilla ML cargada correctamente');
      setCurrentStep(2); // Move to validation step
      
    } catch (error) {
      logger.error('❌ Error analizando plantilla ML:', error);
      setError(error.message || 'Error al analizar la plantilla ML');
      toast.error(`❌ Error: ${error.message || 'No se pudo analizar la plantilla'}`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Step 2: Validate Template
  const handleTemplateValidation = () => {
    const analysis = wizardData.mlTemplateAnalysis;
    
    if (analysis?.analysis?.is_ml_template) {
      toast.success('✅ Plantilla validada correctamente');
      setCurrentStep(3); // Move to category selection
    } else {
      setError('La plantilla no es válida para Mercado Libre');
      toast.error('❌ Plantilla no válida');
    }
  };

  // Step 3: Category Selection
  const handleCategorySelection = (category) => {
    setWizardData(prev => ({
      ...prev,
      selectedCategory: category
    }));
    
    toast.success(`✅ Categoría seleccionada: ${category}`);
    setCurrentStep(4); // Move to default settings
  };

  // Step 4: Default Settings Configuration
  const handleDefaultSettings = (settings) => {
    setWizardData(prev => ({
      ...prev,
      defaultSettings: settings
    }));
    
    toast.success('✅ Configuración guardada');
    setCurrentStep(5); // Move to product upload
  };

  // Step 5: Upload Product File
  const handleProductUpload = useCallback(async (acceptedFiles) => {
    if (!acceptedFiles.length) return;
    
    const file = acceptedFiles[0];
    setIsLoading(true);
    setError(null);

    try {
      logger.info('🔍 Analizando archivo de productos...');
      
      const analysisResult = await fileService.analyzeProductData(file);
      
      logger.info('✅ Análisis de productos completado:', analysisResult);
      
      setWizardData(prev => ({
        ...prev,
        productFile: file,
        productAnalysis: analysisResult
      }));
      
      toast.success(`✅ Productos analizados: ${analysisResult.analysis?.structure?.totalProducts || 0} detectados`);
      setCurrentStep(6); // Move to field mapping
      
    } catch (error) {
      logger.error('❌ Error analizando productos:', error);
      setError(error.message || 'Error al analizar el archivo de productos');
      toast.error(`❌ Error: ${error.message || 'No se pudo analizar el archivo'}`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Step 6: Field Mapping Selection
  const handleFieldMapping = (fieldMappings) => {
    setWizardData(prev => ({
      ...prev,
      fieldMappings: fieldMappings
    }));
    
    toast.success('✅ Mapeo de campos configurado');
    setCurrentStep(7); // Move to final results
  };

  // Navigation functions
  const goToNextStep = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const goToPreviousStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const resetWizard = () => {
    setCurrentStep(1);
    setWizardData({
      mlTemplate: null,
      mlTemplateAnalysis: null,
      selectedCategory: null,
      defaultSettings: {},
      productFile: null,
      productAnalysis: null,
      selectedFields: {},
      finalMapping: null
    });
    setError(null);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Star className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Asistente de Mapeo ML</h1>
            <p className="text-gray-600">Te guiaremos paso a paso para crear tu plantilla de Mercado Libre</p>
          </div>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-between mb-8">
          {steps.map((step, index) => {
            const StepIcon = step.icon;
            const isActive = currentStep === step.id;
            const isCompleted = currentStep > step.id;
            const isAccessible = currentStep >= step.id;

            return (
              <div key={step.id} className="flex flex-col items-center flex-1">
                <div className={clsx(
                  'w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-300',
                  isActive && 'bg-blue-600 border-blue-600 text-white',
                  isCompleted && 'bg-green-600 border-green-600 text-white',
                  !isActive && !isCompleted && isAccessible && 'border-blue-300 text-blue-600',
                  !isAccessible && 'border-gray-300 text-gray-400'
                )}>
                  {isCompleted ? (
                    <Check className="w-6 h-6" />
                  ) : (
                    <StepIcon className="w-6 h-6" />
                  )}
                </div>
                
                <div className="mt-2 text-center">
                  <div className={clsx(
                    'text-sm font-medium',
                    isActive && 'text-blue-600',
                    isCompleted && 'text-green-600',
                    !isActive && !isCompleted && 'text-gray-500'
                  )}>
                    {step.title}
                  </div>
                  <div className="text-xs text-gray-500 mt-1 hidden sm:block">
                    {step.description}
                  </div>
                </div>

                {/* Connector Line */}
                {index < steps.length - 1 && (
                  <div className={clsx(
                    'absolute h-0.5 w-full transform translate-y-6',
                    isCompleted && 'bg-green-300',
                    !isCompleted && 'bg-gray-300'
                  )} style={{ 
                    left: `${(100 / steps.length) * (index + 0.5)}%`, 
                    width: `${100 / steps.length}%`,
                    zIndex: -1 
                  }} />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <span className="text-red-700 font-medium">Error</span>
          </div>
          <p className="text-red-600 mt-2">{error}</p>
          <button
            onClick={() => setError(null)}
            className="mt-3 text-sm text-red-600 hover:text-red-800 font-medium"
          >
            Cerrar
          </button>
        </div>
      )}

      {/* Step Content */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {currentStep === 1 && <Step1MLTemplateUpload onUpload={handleMLTemplateUpload} isLoading={isLoading} />}
        {currentStep === 2 && <Step2TemplateValidation data={wizardData} onValidate={handleTemplateValidation} />}
        {currentStep === 3 && <Step3CategorySelection data={wizardData} onSelect={handleCategorySelection} />}
        {currentStep === 4 && <Step4DefaultSettings data={wizardData} onSave={handleDefaultSettings} />}
        {currentStep === 5 && <Step5ProductUpload onUpload={handleProductUpload} isLoading={isLoading} productAnalysis={wizardData.productAnalysis} />}
        {currentStep === 6 && <Step6FieldMapping data={wizardData} onMap={handleFieldMapping} />}
        {currentStep === 7 && <Step7FinalResults data={wizardData} onReset={resetWizard} />}
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={goToPreviousStep}
          disabled={currentStep === 1}
          className={clsx(
            'flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors',
            currentStep === 1 
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          )}
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Anterior</span>
        </button>

        <button
          onClick={resetWizard}
          className="flex items-center space-x-2 px-4 py-2 rounded-lg font-medium text-gray-600 hover:text-gray-800 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Reiniciar</span>
        </button>

        <button
          onClick={goToNextStep}
          disabled={currentStep === steps.length}
          className={clsx(
            'flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors',
            currentStep === steps.length
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          )}
        >
          <span>Siguiente</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

// Step 1: ML Template Upload Component
const Step1MLTemplateUpload = ({ onUpload, isLoading }) => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: onUpload,
    accept: {
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    multiple: false,
    disabled: isLoading
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Paso 1: Sube tu Plantilla ML</h2>
        <p className="text-gray-600">
          Descarga la plantilla oficial desde tu cuenta de Mercado Libre y súbela aquí para analizarla.
        </p>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">📋 Instrucciones:</h3>
        <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800">
          <li>Ve a tu cuenta de Mercado Libre</li>
          <li>Descarga la plantilla oficial de carga masiva</li>
          <li>Sube el archivo Excel aquí sin modificaciones</li>
          <li>Verificaremos que sea una plantilla válida</li>
        </ol>
      </div>

      {/* Upload Area */}
      <div 
        {...getRootProps()} 
        className={clsx(
          "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
          isDragActive ? "border-blue-400 bg-blue-50" : "border-gray-300 hover:border-gray-400",
          isLoading && "opacity-50 cursor-not-allowed"
        )}
      >
        <input {...getInputProps()} />
        <div className="space-y-4">
          <div className="w-16 h-16 mx-auto bg-blue-100 rounded-full flex items-center justify-center">
            {isLoading ? (
              <Loader className="w-8 h-8 text-blue-600 animate-spin" />
            ) : (
              <FileSpreadsheet className="w-8 h-8 text-blue-600" />
            )}
          </div>
          <div>
            <p className="text-lg font-medium text-gray-900">
              {isLoading ? 'Analizando plantilla...' : 'Arrastra tu plantilla ML aquí'}
            </p>
            <p className="text-gray-600 mt-1">
              {isLoading ? 'Por favor espera...' : 'o haz clic para seleccionar'}
            </p>
          </div>
          <div className="text-sm text-gray-500">
            <p>Formatos soportados: .xlsx, .xls</p>
            <p>Solo plantillas oficiales de Mercado Libre</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Step 2: Template Validation Component
const Step2TemplateValidation = ({ data, onValidate }) => {
  const analysis = data.mlTemplateAnalysis?.analysis;
  const validation = data.mlTemplateAnalysis?.validation;
  
  if (!analysis) {
    return (
      <div className="space-y-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Paso 2: Validación de Plantilla</h2>
        <div className="text-center text-gray-500 py-8">
          <AlertCircle className="w-12 h-12 mx-auto text-gray-300 mb-4" />
          <p>No hay datos de análisis disponibles</p>
        </div>
      </div>
    );
  }

  const isValid = validation?.is_ml_template;
  const confidence = validation?.confidence_score || 0;
  const recommendations = data.mlTemplateAnalysis?.recommendations || [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Paso 2: Validación de Plantilla</h2>
        <p className="text-gray-600">
          Hemos analizado tu plantilla y verificado que sea compatible con Mercado Libre.
        </p>
      </div>

      {/* Validation Results */}
      <div className={clsx(
        "rounded-lg border-2 p-6",
        isValid ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"
      )}>
        <div className="flex items-center space-x-3 mb-4">
          {isValid ? (
            <CheckCircle className="w-8 h-8 text-green-600" />
          ) : (
            <XCircle className="w-8 h-8 text-red-600" />
          )}
          <div>
            <h3 className={clsx(
              "text-lg font-semibold",
              isValid ? "text-green-900" : "text-red-900"
            )}>
              {isValid ? "✅ Plantilla Válida" : "❌ Plantilla No Válida"}
            </h3>
            <p className={clsx(
              "text-sm",
              isValid ? "text-green-700" : "text-red-700"
            )}>
              Confianza: {(confidence * 100).toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Analysis Details */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="bg-white rounded p-3 border">
            <div className="text-sm text-gray-600">Campos ML Detectados</div>
            <div className="text-xl font-semibold text-gray-900">
              {validation?.field_count || 0}
            </div>
          </div>
          <div className="bg-white rounded p-3 border">
            <div className="text-sm text-gray-600">Categorías Encontradas</div>
            <div className="text-xl font-semibold text-gray-900">
              {validation?.category_count || 0}
            </div>
          </div>
          <div className="bg-white rounded p-3 border">
            <div className="text-sm text-gray-600">Estructura</div>
            <div className={clsx(
              "text-xl font-semibold",
              validation?.structure_valid ? "text-green-600" : "text-red-600"
            )}>
              {validation?.structure_valid ? "✓ Válida" : "✗ Inválida"}
            </div>
          </div>
        </div>

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Recomendaciones:</h4>
            <ul className="space-y-1">
              {recommendations.map((rec, index) => (
                <li key={index} className="text-sm text-gray-700 flex items-start space-x-2">
                  <span className="text-blue-500 mt-1">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Detected Fields */}
      {analysis.ml_fields && analysis.ml_fields.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">🎯 Campos ML Detectados:</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {analysis.ml_fields.slice(0, 8).map((field, index) => (
              <div key={index} className="bg-white rounded p-3 border border-gray-200">
                <div className="font-medium text-gray-900">{field.field_name}</div>
                <div className="text-sm text-gray-600">{field.detected_text}</div>
                <div className="text-xs text-gray-500 mt-1">{field.position}</div>
              </div>
            ))}
          </div>
          {analysis.ml_fields.length > 8 && (
            <p className="text-sm text-gray-600 mt-3">
              ... y {analysis.ml_fields.length - 8} campos más
            </p>
          )}
        </div>
      )}

      {/* Categories */}
      {analysis.categories && analysis.categories.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">📂 Categorías Detectadas:</h4>
          <div className="flex flex-wrap gap-2">
            {analysis.categories.slice(0, 5).map((category, index) => (
              <span 
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {category.category_name}
              </span>
            ))}
            {analysis.categories.length > 5 && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                +{analysis.categories.length - 5} más
              </span>
            )}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-center">
        {isValid ? (
          <button
            onClick={onValidate}
            className="flex items-center space-x-2 bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors"
          >
            <CheckCircle className="w-5 h-5" />
            <span>Continuar con Plantilla Válida</span>
          </button>
        ) : (
          <div className="text-center">
            <p className="text-red-600 mb-4">
              La plantilla no es válida. Por favor, sube una plantilla oficial de Mercado Libre.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="flex items-center space-x-2 bg-gray-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors mx-auto"
            >
              <RefreshCw className="w-5 h-5" />
              <span>Subir Nueva Plantilla</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Step 3: Category Selection Component
const Step3CategorySelection = ({ data, onSelect }) => {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const analysis = data.mlTemplateAnalysis?.analysis;
  const categories = analysis?.categories || [];

  const handleCategorySelect = (category) => {
    setSelectedCategory(category);
  };

  const handleConfirmSelection = () => {
    if (selectedCategory) {
      onSelect(selectedCategory);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Paso 3: Seleccionar Categoría</h2>
        <p className="text-gray-600">
          Elige la categoría de productos que vas a procesar en esta sesión. Solo puedes seleccionar una categoría por archivo.
        </p>
      </div>

      {/* Category Selection */}
      {categories.length > 0 ? (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">📂 Categorías Detectadas en tu Plantilla:</h3>
            <p className="text-sm text-blue-800">
              Hemos encontrado {categories.length} categoría(s) en tu plantilla. Selecciona la que corresponde a tus productos.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {categories.map((category, index) => (
              <div
                key={index}
                onClick={() => handleCategorySelect(category)}
                className={clsx(
                  "border-2 rounded-lg p-4 cursor-pointer transition-all duration-200",
                  selectedCategory === category
                    ? "border-blue-500 bg-blue-50 shadow-md"
                    : "border-gray-200 hover:border-gray-300 hover:shadow-sm"
                )}
              >
                <div className="flex items-start space-x-3">
                  <div className={clsx(
                    "w-5 h-5 rounded-full border-2 mt-1 flex items-center justify-center",
                    selectedCategory === category
                      ? "border-blue-500 bg-blue-500"
                      : "border-gray-300"
                  )}>
                    {selectedCategory === category && (
                      <Check className="w-3 h-3 text-white" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      {category.category_name}
                    </h4>
                    <p className="text-sm text-gray-600 mb-2">
                      Detectado como: "{category.detected_text}"
                    </p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>📍 {category.position}</span>
                      <span className={clsx(
                        "px-2 py-1 rounded",
                        category.confidence >= 0.8 ? "bg-green-100 text-green-800" :
                        category.confidence >= 0.6 ? "bg-yellow-100 text-yellow-800" :
                        "bg-red-100 text-red-800"
                      )}>
                        {category.confidence >= 0.8 ? "Alta confianza" :
                         category.confidence >= 0.6 ? "Confianza media" : "Baja confianza"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Confirmation */}
          {selectedCategory && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <h4 className="font-medium text-green-900">Categoría Seleccionada</h4>
              </div>
              <p className="text-green-800 mb-3">
                <strong>{selectedCategory.category_name}</strong>
              </p>
              <p className="text-sm text-green-700 mb-4">
                Todos los productos de tu archivo serán clasificados en esta categoría.
              </p>
              <button
                onClick={handleConfirmSelection}
                className="bg-green-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors"
              >
                Confirmar Categoría
              </button>
            </div>
          )}
        </div>
      ) : (
        // Manual Category Input
        <div className="space-y-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <AlertCircle className="w-5 h-5 text-yellow-600" />
              <h3 className="font-semibold text-yellow-900">No se detectaron categorías automáticamente</h3>
            </div>
            <p className="text-yellow-800 mb-3">
              No pudimos detectar categorías específicas en tu plantilla. Puedes seleccionar manualmente o usar una categoría genérica.
            </p>
          </div>

          <div className="bg-white border rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3">Seleccionar Categoría Manualmente:</h4>
            
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Categoría de Mercado Libre
              </label>
              <select
                value={selectedCategory?.category_name || ''}
                onChange={(e) => {
                  if (e.target.value) {
                    setSelectedCategory({
                      category_name: e.target.value,
                      detected_text: 'Selección manual',
                      position: 'Manual',
                      confidence: 1.0
                    });
                  }
                }}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Selecciona una categoría...</option>
                <option value="Electrónicos, Audio y Video">Electrónicos, Audio y Video</option>
                <option value="Celulares y Teléfonos">Celulares y Teléfonos</option>
                <option value="Computación">Computación</option>
                <option value="Casa, Muebles y Jardín">Casa, Muebles y Jardín</option>
                <option value="Ropa y Accesorios">Ropa y Accesorios</option>
                <option value="Deportes y Fitness">Deportes y Fitness</option>
                <option value="Herramientas">Herramientas</option>
                <option value="Libros, Revistas y Comics">Libros, Revistas y Comics</option>
                <option value="Salud y Belleza">Salud y Belleza</option>
                <option value="Juegos y Juguetes">Juegos y Juguetes</option>
                <option value="Otros">Otros</option>
              </select>
            </div>

            {selectedCategory && (
              <div className="mt-4 p-3 bg-blue-50 rounded border border-blue-200">
                <p className="text-blue-800">
                  <strong>Categoría seleccionada:</strong> {selectedCategory.category_name}
                </p>
                <button
                  onClick={handleConfirmSelection}
                  className="mt-2 bg-blue-600 text-white px-4 py-2 rounded font-medium hover:bg-blue-700 transition-colors"
                >
                  Confirmar Categoría
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Info Section */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">💡 ¿Por qué solo una categoría?</h4>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• Mercado Libre requiere configuraciones específicas por categoría</li>
          <li>• Cada categoría tiene campos y requisitos diferentes</li>
          <li>• Es más fácil revisar y validar productos de la misma categoría</li>
          <li>• Puedes procesar múltiples categorías en sesiones separadas</li>
        </ul>
      </div>
    </div>
  );
};
// Step 4: Default Settings Configuration Component
const Step4DefaultSettings = ({ data, onSave }) => {
  const [settings, setSettings] = useState({
    condition: 'new', // new, used, refurbished
    currency: 'ARS',
    free_shipping: 'yes',
    accepts_mercado_pago: 'yes',
    pickup_allowed: 'no',
    flex_shipping: 'no',
    listing_type: 'gold_special', // gold_special, gold_pro, free
    warranty: '',
    brand: '',
    default_description: ''
  });

  const [customDefaults, setCustomDefaults] = useState([]);

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const addCustomDefault = () => {
    setCustomDefaults(prev => [...prev, { field: '', value: '' }]);
  };

  const updateCustomDefault = (index, field, value) => {
    setCustomDefaults(prev => 
      prev.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    );
  };

  const removeCustomDefault = (index) => {
    setCustomDefaults(prev => prev.filter((_, i) => i !== index));
  };

  const handleSaveSettings = () => {
    const finalSettings = {
      ...settings,
      custom_defaults: customDefaults.filter(item => item.field && item.value)
    };
    onSave(finalSettings);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Paso 4: Configuración por Defecto</h2>
        <p className="text-gray-600">
          Define los valores que se aplicarán automáticamente a todos tus productos. Esto te ahorrará tiempo al no tener que configurar cada producto individualmente.
        </p>
      </div>

      {/* Category Context */}
      {data.selectedCategory && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-1">📂 Categoría Seleccionada:</h3>
          <p className="text-blue-800">{data.selectedCategory.category_name}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Basic Settings */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900 border-b pb-2">Configuración Básica</h3>
          
          {/* Condition */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Estado del Producto *
            </label>
            <select
              value={settings.condition}
              onChange={(e) => handleSettingChange('condition', e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="new">Nuevo</option>
              <option value="used">Usado</option>
              <option value="refurbished">Reacondicionado</option>
            </select>
          </div>

          {/* Currency */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Moneda *
            </label>
            <select
              value={settings.currency}
              onChange={(e) => handleSettingChange('currency', e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="ARS">Peso Argentino (ARS)</option>
              <option value="USD">Dólar Estadounidense (USD)</option>
            </select>
          </div>

          {/* Listing Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Publicación *
            </label>
            <select
              value={settings.listing_type}
              onChange={(e) => handleSettingChange('listing_type', e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="gold_special">Clásica</option>
              <option value="gold_pro">Premium</option>
              <option value="free">Gratuita</option>
            </select>
          </div>
        </div>

        {/* Shipping & Payment Settings */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900 border-b pb-2">Envío y Pago</h3>
          
          {/* Free Shipping */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Envío Gratis
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="yes"
                  checked={settings.free_shipping === 'yes'}
                  onChange={(e) => handleSettingChange('free_shipping', e.target.value)}
                  className="mr-2"
                />
                Sí
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="no"
                  checked={settings.free_shipping === 'no'}
                  onChange={(e) => handleSettingChange('free_shipping', e.target.value)}
                  className="mr-2"
                />
                No
              </label>
            </div>
          </div>

          {/* Mercado Pago */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Acepta Mercado Pago
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="yes"
                  checked={settings.accepts_mercado_pago === 'yes'}
                  onChange={(e) => handleSettingChange('accepts_mercado_pago', e.target.value)}
                  className="mr-2"
                />
                Sí
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="no"
                  checked={settings.accepts_mercado_pago === 'no'}
                  onChange={(e) => handleSettingChange('accepts_mercado_pago', e.target.value)}
                  className="mr-2"
                />
                No
              </label>
            </div>
          </div>

          {/* Pickup */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Retiro en Persona
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="yes"
                  checked={settings.pickup_allowed === 'yes'}
                  onChange={(e) => handleSettingChange('pickup_allowed', e.target.value)}
                  className="mr-2"
                />
                Sí
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="no"
                  checked={settings.pickup_allowed === 'no'}
                  onChange={(e) => handleSettingChange('pickup_allowed', e.target.value)}
                  className="mr-2"
                />
                No
              </label>
            </div>
          </div>

          {/* Flex Shipping */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Envío Flex
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="yes"
                  checked={settings.flex_shipping === 'yes'}
                  onChange={(e) => handleSettingChange('flex_shipping', e.target.value)}
                  className="mr-2"
                />
                Sí
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="no"
                  checked={settings.flex_shipping === 'no'}
                  onChange={(e) => handleSettingChange('flex_shipping', e.target.value)}
                  className="mr-2"
                />
                No
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Fields */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900 border-b pb-2">Información Adicional</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Marca por Defecto (opcional)
            </label>
            <input
              type="text"
              value={settings.brand}
              onChange={(e) => handleSettingChange('brand', e.target.value)}
              placeholder="Ej: Samsung, Apple, Nike..."
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Garantía por Defecto (opcional)
            </label>
            <input
              type="text"
              value={settings.warranty}
              onChange={(e) => handleSettingChange('warranty', e.target.value)}
              placeholder="Ej: 12 meses, Sin garantía..."
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Descripción Base (opcional)
          </label>
          <textarea
            value={settings.default_description}
            onChange={(e) => handleSettingChange('default_description', e.target.value)}
            placeholder="Texto que se agregará a todas las descripciones..."
            rows={3}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Custom Defaults */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">Campos Personalizados</h3>
          <button
            onClick={addCustomDefault}
            className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 font-medium"
          >
            <Star className="w-4 h-4" />
            <span>Agregar Campo</span>
          </button>
        </div>

        {customDefaults.map((custom, index) => (
          <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded border">
            <input
              type="text"
              placeholder="Nombre del campo..."
              value={custom.field}
              onChange={(e) => updateCustomDefault(index, 'field', e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
            <input
              type="text"
              placeholder="Valor por defecto..."
              value={custom.value}
              onChange={(e) => updateCustomDefault(index, 'value', e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              onClick={() => removeCustomDefault(index)}
              className="text-red-600 hover:text-red-800"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        ))}
      </div>

      {/* Preview */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">👀 Vista Previa de Configuración:</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
          <div><strong>Estado:</strong> {settings.condition === 'new' ? 'Nuevo' : settings.condition === 'used' ? 'Usado' : 'Reacondicionado'}</div>
          <div><strong>Moneda:</strong> {settings.currency}</div>
          <div><strong>Envío gratis:</strong> {settings.free_shipping === 'yes' ? 'Sí' : 'No'}</div>
          <div><strong>Mercado Pago:</strong> {settings.accepts_mercado_pago === 'yes' ? 'Sí' : 'No'}</div>
          <div><strong>Retiro:</strong> {settings.pickup_allowed === 'yes' ? 'Sí' : 'No'}</div>
          <div><strong>Flex:</strong> {settings.flex_shipping === 'yes' ? 'Sí' : 'No'}</div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-center">
        <button
          onClick={handleSaveSettings}
          className="flex items-center space-x-2 bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          <Settings className="w-5 h-5" />
          <span>Guardar Configuración</span>
        </button>
      </div>
    </div>
  );
};
// Step 5: Product File Upload Component
const Step5ProductUpload = ({ onUpload, isLoading, productAnalysis }) => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: onUpload,
    accept: {
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv']
    },
    multiple: false,
    disabled: isLoading
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Paso 5: Sube tus Productos</h2>
        <p className="text-gray-600">
          Ahora sube el archivo con los datos de tus productos que quieres mapear a la plantilla ML.
        </p>
      </div>

      {/* Instructions */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 className="font-semibold text-green-900 mb-2">📋 Formatos Aceptados:</h3>
        <ul className="list-disc list-inside space-y-1 text-sm text-green-800">
          <li><strong>Excel (.xlsx, .xls):</strong> Datos organizados en columnas</li>
          <li><strong>CSV (.csv):</strong> Datos separados por comas</li>
          <li>Primera fila debe contener los nombres de columnas</li>
          <li>Cada fila representa un producto diferente</li>
        </ul>
      </div>

      {/* Upload Area */}
      <div 
        {...getRootProps()} 
        className={clsx(
          "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
          isDragActive ? "border-green-400 bg-green-50" : "border-gray-300 hover:border-gray-400",
          isLoading && "opacity-50 cursor-not-allowed"
        )}
      >
        <input {...getInputProps()} />
        <div className="space-y-4">
          <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
            {isLoading ? (
              <Loader className="w-8 h-8 text-green-600 animate-spin" />
            ) : (
              <Upload className="w-8 h-8 text-green-600" />
            )}
          </div>
          <div>
            <p className="text-lg font-medium text-gray-900">
              {isLoading ? 'Analizando productos...' : 'Arrastra tu archivo de productos aquí'}
            </p>
            <p className="text-gray-600 mt-1">
              {isLoading ? 'Detectando campos y estructura...' : 'o haz clic para seleccionar'}
            </p>
          </div>
          <div className="text-sm text-gray-500">
            <p>Formatos: .xlsx, .xls, .csv (máx. 10MB)</p>
          </div>
        </div>
      </div>

      {/* Product Analysis Results */}
      {productAnalysis && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-3">📊 Análisis de Productos:</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="bg-white rounded p-3">
              <div className="text-blue-600 font-medium">Total Productos</div>
              <div className="text-2xl font-bold text-gray-900">{productAnalysis?.analysis?.structure?.totalProducts || 0}</div>
            </div>
            <div className="bg-white rounded p-3">
              <div className="text-blue-600 font-medium">Campos Detectados</div>
              <div className="text-2xl font-bold text-gray-900">{productAnalysis?.analysis?.structure?.fieldsDetected || 0}</div>
            </div>
            <div className="bg-white rounded p-3">
              <div className="text-blue-600 font-medium">Compatibilidad</div>
              <div className="text-2xl font-bold text-green-600">{productAnalysis?.analysis?.structure?.compatibility || '0%'}</div>
            </div>
            <div className="bg-white rounded p-3">
              <div className="text-blue-600 font-medium">Estado</div>
              <div className="text-sm font-medium text-green-600">✅ Listo para mapeo</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
// Step 6: Field Mapping Component
const Step6FieldMapping = ({ data, onMap }) => {
  const [mappings, setMappings] = useState({});
  const [previewData, setPreviewData] = useState([]);

  // ML Template fields from the analysis
  const mlFields = data?.mlTemplateAnalysis?.analysis?.ml_fields || [];
  
  // Product file fields from the analysis  
  const productFields = data?.productAnalysis?.analysis?.structure?.fields || [];

  const handleFieldMapping = (mlField, productField) => {
    setMappings(prev => ({
      ...prev,
      [mlField]: productField
    }));
  };

  const handleAutoMapping = () => {
    const autoMappings = {};
    
    mlFields.forEach(mlField => {
      // Simple auto-mapping logic based on field name similarity
      const fieldName = mlField.field_name.toLowerCase();
      
      const bestMatch = productFields.find(pField => {
        const pFieldLower = pField.toLowerCase();
        
        // Direct matches
        if (pFieldLower.includes('título') || pFieldLower.includes('title')) return fieldName.includes('título');
        if (pFieldLower.includes('precio') || pFieldLower.includes('price')) return fieldName.includes('precio');
        if (pFieldLower.includes('stock') || pFieldLower.includes('cantidad')) return fieldName.includes('stock');
        if (pFieldLower.includes('categoría') || pFieldLower.includes('category')) return fieldName.includes('categoría');
        
        return false;
      });
      
      if (bestMatch) {
        autoMappings[mlField.field_name] = bestMatch;
      }
    });
    
    setMappings(autoMappings);
    toast.success(`🤖 Auto-mapeo completado: ${Object.keys(autoMappings).length} campos mapeados`);
  };

  const handleSaveMapping = () => {
    const mappingCount = Object.keys(mappings).length;
    if (mappingCount === 0) {
      toast.error('⚠️ Debes mapear al menos un campo');
      return;
    }
    
    onMap(mappings);
    toast.success(`✅ Mapeo guardado: ${mappingCount} campos configurados`);
  };

  const generatePreview = () => {
    // Generate preview of first 3 products with current mapping
    const preview = data?.productAnalysis?.analysis?.sampleData?.slice(0, 3) || [];
    setPreviewData(preview);
  };

  useEffect(() => {
    generatePreview();
  }, [mappings, data]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Paso 6: Mapeo de Campos</h2>
        <p className="text-gray-600">
          Conecta los campos de tus productos con los campos de la plantilla de Mercado Libre.
        </p>
      </div>

      {/* Auto-mapping Button */}
      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-600">
          <span className="font-medium">{mlFields.length}</span> campos ML disponibles • 
          <span className="font-medium ml-1">{productFields.length}</span> campos de productos detectados
        </div>
        <button
          onClick={handleAutoMapping}
          className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-700 transition-colors"
        >
          <Star className="w-4 h-4" />
          <span>Auto-mapeo Inteligente</span>
        </button>
      </div>

      {/* Mapping Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ML Fields Column */}
        <div className="space-y-4">
          <h3 className="font-semibold text-gray-900 border-b pb-2">📋 Campos Mercado Libre</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {mlFields.map((mlField, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{mlField.field_name}</div>
                    <div className="text-sm text-gray-600">{mlField.description}</div>
                  </div>
                  <div className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {(mlField.confidence * 100).toFixed(0)}% conf.
                  </div>
                </div>
                
                <select
                  value={mappings[mlField.field_name] || ''}
                  onChange={(e) => handleFieldMapping(mlField.field_name, e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">-- Seleccionar campo --</option>
                  {productFields.map((field, idx) => (
                    <option key={idx} value={field}>{field}</option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        </div>

        {/* Preview Column */}
        <div className="space-y-4">
          <h3 className="font-semibold text-gray-900 border-b pb-2">👀 Vista Previa</h3>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3">Mapeos Actuales:</h4>
            <div className="space-y-2 text-sm">
              {Object.entries(mappings).map(([mlField, productField]) => (
                <div key={mlField} className="flex items-center justify-between bg-white p-2 rounded border">
                  <span className="font-medium text-blue-600">{mlField}</span>
                  <span className="text-gray-600">→</span>
                  <span className="text-green-600">{productField}</span>
                </div>
              ))}
              {Object.keys(mappings).length === 0 && (
                <div className="text-gray-500 italic">No hay mapeos configurados</div>
              )}
            </div>
          </div>

          {/* Sample Data Preview */}
          {previewData.length > 0 && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">📊 Muestra de Datos:</h4>
              <div className="space-y-2 text-xs">
                {previewData.map((product, idx) => (
                  <div key={idx} className="bg-white p-2 rounded border">
                    <div className="font-medium text-gray-700">Producto {idx + 1}:</div>
                    {Object.entries(mappings).map(([mlField, productField]) => (
                      <div key={mlField} className="text-gray-600">
                        <span className="font-medium">{mlField}:</span> {product[productField] || 'N/A'}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Progress and Save */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="font-medium text-blue-900">
              Progreso del Mapeo: {Object.keys(mappings).length} / {mlFields.length} campos
            </div>
            <div className="text-sm text-blue-700">
              {((Object.keys(mappings).length / mlFields.length) * 100).toFixed(0)}% completado
            </div>
          </div>
          <button
            onClick={handleSaveMapping}
            className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            <ArrowRight className="w-4 h-4" />
            <span>Continuar al Resumen</span>
          </button>
        </div>
      </div>
    </div>
  );
};
// Step 7: Final Results Component
const Step7FinalResults = ({ data, onReset }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [writeMode, setWriteMode] = useState('fill-empty');
  const [interactiveEdits, setInteractiveEdits] = useState('');

  const mlFields = data?.mlTemplateAnalysis?.analysis?.ml_fields || [];
  const mappings = data?.fieldMappings || {};
  const productCount = data?.productAnalysis?.analysis?.structure?.totalProducts || 0;
  const mappedFieldsCount = Object.keys(mappings).length;

  const handlePreviewGenerated = (result) => {
    setPreviewData(result);
    logger.info('🔍 Vista previa generada:', result);
  };

  const handleGenerateFile = async () => {
    setIsGenerating(true);

    try {
      logger.info('🔄 Generando archivo ML...', {
        mlTemplate: data?.mlTemplate?.name,
        productData: data?.productData?.name,
        mappings: Object.keys(mappings).length,
        settings: data?.defaultSettings
      });

      // Prepare edits payload if interactive
      let editsPayload = null;
      if (writeMode === 'interactive' && interactiveEdits) {
        let parsed = null;
        try {
          parsed = JSON.parse(interactiveEdits);
        } catch (err) {
          toast.error('Edits JSON inválido');
          setIsGenerating(false);
          return;
        }

  // use shared mapHeaderToLogical

        const invalid = [];
        editsPayload = [];
        parsed.forEach((e) => {
          const logical = mapHeaderToLogical(e.field);
          if (!logical) invalid.push(e.field);
          else editsPayload.push({ row: e.row, field: logical, value: e.value });
        });

        if (invalid.length > 0) {
          toast.error(`Encabezados desconocidos en edits: ${[...new Set(invalid)].join(', ')}`);
          setIsGenerating(false);
          return;
        }
      }

      // Transform mappings into backend-shaped mapping: { "Etiqueta ML": "SourceColumn" }
      const backendMapping = {};
      try {
        Object.entries(mappings).forEach(([mlLabel, productField]) => {
          if (!productField) return;
          // use the mlLabel as-is (it's the visible ML field name from analyzer)
          backendMapping[mlLabel] = productField;
        });
      } catch (err) {
        logger.warn('Error building backend mapping payload', err);
      }

      // Validate presence of required logical fields (title, price)
      const requiredLogical = ['title', 'price'];
      const mappedLogical = new Set();
      Object.keys(backendMapping).forEach((mlLabel) => {
        const logical = mapHeaderToLogical(mlLabel);
        if (logical) mappedLogical.add(logical);
      });

      const missing = requiredLogical.filter(r => !mappedLogical.has(r));
      if (missing.length > 0) {
        toast.error(`Faltan campos requeridos mapeados: ${missing.join(', ')} — mapea al menos Título y Precio antes de generar`);
        setIsGenerating(false);
        return;
      }

      const result = await fileService.generateMLFile(
        data.mlTemplate,
        data.productFile,
        backendMapping,
        data.defaultSettings || {},
        null,
        writeMode,
        editsPayload
      );

      logger.info('✅ Archivo generado:', result);

      toast.success(`✅ Archivo ML generado: ${result.file_info?.products_processed || 0} productos procesados`);
      setDownloadUrl(result.download?.url);

    } catch (error) {
      logger.error('❌ Error generando archivo:', error);
      toast.error(`❌ Error: ${error.response?.data?.detail || error.message || 'No se pudo generar el archivo'}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleWriteModeChange = (e) => setWriteMode(e.target.value);

  const handleDownload = async () => {
    if (!downloadUrl) return;
    
    try {
      // Extract filename from download URL
      const filename = downloadUrl.split('/').pop();
      
      logger.info('📥 Iniciando descarga:', filename);
      
      await fileService.downloadMLFile(filename);
      toast.success('📥 Descarga completada');
      
    } catch (error) {
      logger.error('❌ Error descargando:', error);
      toast.error(`❌ Error en descarga: ${error.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Paso 7: Vista Previa y Descarga</h2>
        <p className="text-gray-600">
          ¡Perfecto! Revisa la vista previa de tu archivo final antes de descargarlo.
        </p>
      </div>

      {/* Success Summary */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
            <Check className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-green-900">¡Mapeo Completado!</h3>
            <p className="text-green-700">Tu plantilla ML está lista para cargar productos</p>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{productCount}</div>
            <div className="text-sm text-gray-600">Productos</div>
          </div>
          <div className="bg-white rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{mappedFieldsCount}</div>
            <div className="text-sm text-gray-600">Campos Mapeados</div>
          </div>
          <div className="bg-white rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">{Math.round((mappedFieldsCount / mlFields.length) * 100)}%</div>
            <div className="text-sm text-gray-600">Completitud</div>
          </div>
          <div className="bg-white rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-orange-600">ML</div>
            <div className="text-sm text-gray-600">Compatible</div>
          </div>
        </div>
      </div>

      {/* ML File Preview Component */}
      <MLFilePreview
        mlTemplate={data.mlTemplate}
        productData={data.productFile}
        mappingConfig={mappings}
        defaultSettings={data.defaultSettings || {}}
        onPreviewGenerated={handlePreviewGenerated}
        onGenerateFile={() => handleGenerateFile()}
      />

      {/* Mapping review panel */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h4 className="font-semibold mb-2">Revisión de Mapeo (ML → Columna Fuente)</h4>
        <div className="text-sm text-gray-700 mb-3">Revisa las etiquetas de Mercado Libre y la columna fuente que serán enviadas al backend.</div>
        <div className="space-y-2 max-h-40 overflow-y-auto">
          {Object.entries(mappings).length === 0 && (
            <div className="text-gray-500 italic">No hay mapeos configurados</div>
          )}
          {Object.entries(mappings).map(([mlLabel, src]) => (
            <div key={mlLabel} className="flex items-center justify-between bg-gray-50 p-2 rounded border">
              <div className="font-medium text-gray-800">{mlLabel}</div>
              <div className="text-sm text-gray-600">{src || 'Sin mapear'}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Write mode selector and interactive edits */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h4 className="font-semibold mb-2">Modo de escritura</h4>
        <div className="flex items-center space-x-3 mb-3">
          <select value={writeMode} onChange={handleWriteModeChange} className="border rounded p-2">
            <option value="fill-empty">Llenar celdas vacías (seguro)</option>
            <option value="append">Agregar al final (append)</option>
            <option value="interactive">Edición interactiva (aplicar edits)</option>
            <option value="overwrite">Sobrescribir (requiere backup)</option>
          </select>
          <button
            onClick={() => handleGenerateFile()}
            disabled={isGenerating}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            {isGenerating ? 'Generando...' : 'Generar Archivo'}
          </button>
        </div>

        {writeMode === 'interactive' && (
          <div>
            <label className="block text-sm font-medium mb-1">Edits (JSON):</label>
            <textarea
              value={interactiveEdits}
              onChange={(e) => setInteractiveEdits(e.target.value)}
              placeholder='[ { "row": 12, "field": "title", "value": "Nuevo título" } ]'
              className="w-full border rounded p-2 h-28 font-mono text-sm"
            />
            <p className="text-xs text-gray-500 mt-1">Proporciona una lista JSON de ediciones a aplicar. Las filas deben ser &gt;= 8.</p>
          </div>
        )}
      </div>

      {/* Configuration Applied */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-3">⚙️ Configuración Aplicada:</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
          <div><strong>Categoría:</strong> {data?.selectedCategory || 'No especificada'}</div>
          <div><strong>Estado:</strong> {data?.defaultSettings?.condition || 'Nuevo'}</div>
          <div><strong>Moneda:</strong> {data?.defaultSettings?.currency || 'ARS'}</div>
          <div><strong>Envío gratis:</strong> {data?.defaultSettings?.free_shipping === 'yes' ? 'Sí' : 'No'}</div>
          <div><strong>Mercado Pago:</strong> {data?.defaultSettings?.accepts_mercado_pago === 'yes' ? 'Sí' : 'No'}</div>
          <div><strong>Retiro:</strong> {data?.defaultSettings?.pickup_allowed === 'yes' ? 'Sí' : 'No'}</div>
        </div>
      </div>

      {/* Download Status */}
      {downloadUrl && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Check className="w-6 h-6 text-green-600" />
              <div>
                <h3 className="text-lg font-semibold text-green-900">¡Archivo Generado!</h3>
                <p className="text-green-700">Tu archivo ML está listo para descargar</p>
              </div>
            </div>
            <button
              onClick={handleDownload}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              📥 Descargar Archivo
            </button>
          </div>
        </div>
      )}

      {/* Generation Status */}
      {isGenerating && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <div>
              <h3 className="text-lg font-semibold text-blue-900">Generando Archivo...</h3>
              <p className="text-blue-700">Procesando {productCount} productos con tus configuraciones</p>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <button
          onClick={onReset}
          className="flex items-center space-x-2 bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors"
        >
          <RefreshCw className="w-5 h-5" />
          <span>Procesar Otro Archivo</span>
        </button>
      </div>

      {/* Tips */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h4 className="font-semibold text-yellow-900 mb-2">💡 Próximos Pasos:</h4>
        <ol className="list-decimal list-inside space-y-1 text-sm text-yellow-800">
          <li>Revisa la vista previa de tus productos</li>
          <li>Ajusta el mapeo si es necesario</li>
          <li>Descarga el archivo generado (.xlsx)</li>
          <li>Ve a tu cuenta de Mercado Libre</li>
          <li>Sube el archivo en "Publicar" → "Carga Masiva"</li>
          <li>¡Tus productos estarán online!</li>
        </ol>
      </div>
    </div>
  );
};

export default MLMappingWizard;
