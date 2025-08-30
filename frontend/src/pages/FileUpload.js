import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useAuth } from '../context/AuthContext';
import { fileService } from '../services/fileService';
import { logger } from '../utils/logger';
import { 
  Upload, 
  FileText, 
  FileSpreadsheet, 
  File, 
  X, 
  Check, 
  AlertCircle,
  Loader,
  Download,
  Eye
} from 'lucide-react';
import { clsx } from 'clsx';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

const FileUpload = () => {
  const { isPremium } = useAuth();
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback(async (acceptedFiles) => {
    for (const file of acceptedFiles) {
      // Validate file size (5MB for free, 50MB for premium)
      const maxSize = isPremium ? 50 * 1024 * 1024 : 5 * 1024 * 1024;
      if (file.size > maxSize) {
        toast.error(`Archivo demasiado grande. Máximo ${isPremium ? '50MB' : '5MB'}`);
        continue;
      }

      // Add file to list
      const fileItem = {
        id: Date.now() + Math.random(),
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        status: 'uploading',
        progress: 0,
        result: null,
      };

      setUploadedFiles(prev => [...prev, fileItem]);

      try {
        setIsProcessing(true);
        
        // Upload file
        const result = await fileService.uploadFile(file, {
          onProgress: (progress) => {
            setUploadProgress(progress);
            setUploadedFiles(prev => 
              prev.map(f => 
                f.id === fileItem.id 
                  ? { ...f, progress } 
                  : f
              )
            );
          },
        });

        // Update file status
        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === fileItem.id 
              ? { 
                  ...f, 
                  status: result.success ? 'completed' : 'error',
                  result: result,
                  progress: 100
                } 
              : f
          )
        );

        if (result.success) {
          toast.success(`${file.name} procesado exitosamente`);
        } else {
          toast.error(`Error procesando ${file.name}: ${result.error}`);
        }

      } catch (error) {
        logger.error('Upload error:', error);
        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === fileItem.id 
              ? { 
                  ...f, 
                  status: 'error',
                  result: { error: error.message || 'Error desconocido' }
                } 
              : f
          )
        );
        toast.error(`Error subiendo ${file.name}`);
      } finally {
        setIsProcessing(false);
        setUploadProgress(0);
      }
    }
  }, [isPremium]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: isPremium ? 10 : 3,
    multiple: true,
  });

  const getFileIcon = (type) => {
    if (type.includes('spreadsheet') || type.includes('csv')) {
      return FileSpreadsheet;
    }
    if (type.includes('pdf')) {
      return FileText;
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
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const downloadResult = async (file) => {
    if (!file.result?.task_id) return;
    
    try {
      await fileService.downloadFile(file.result.task_id, `processed_${file.name}`);
      toast.success('Descarga iniciada');
    } catch (error) {
      toast.error('Error al descargar archivo');
    }
  };

  const viewPreview = (file) => {
    // Open preview modal or navigate to preview page
    toast.info('Vista previa próximamente');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-secondary-900">
              Subir Archivos
            </h1>
            <p className="text-secondary-600 mt-1">
              Carga tus archivos Excel, CSV, PDF o Word para procesarlos
            </p>
          </div>
          
          {/* Limits Badge */}
          <div className="text-right">
            <div className="text-sm text-secondary-600">
              Límites de tu cuenta:
            </div>
            <div className="text-lg font-semibold text-primary-600">
              {isPremium ? '50MB • 10 archivos' : '5MB • 3 archivos'}
            </div>
          </div>
        </div>
      </div>

      {/* Upload Zone */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-secondary-900">
            Zona de Carga
          </h2>
          <p className="text-sm text-secondary-600">
            Arrastra archivos aquí o haz clic para seleccionar
          </p>
        </div>
        
        <div className="card-body">
          <div
            {...getRootProps()}
            className={clsx(
              'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300',
              isDragActive 
                ? 'border-primary-500 bg-primary-50' 
                : 'border-secondary-300 hover:border-primary-400 hover:bg-primary-25'
            )}
          >
            <input {...getInputProps()} />
            
            <div className="space-y-4">
              <div className="w-16 h-16 mx-auto bg-primary-100 rounded-full flex items-center justify-center">
                <Upload className={clsx(
                  'w-8 h-8 transition-colors',
                  isDragActive ? 'text-primary-600' : 'text-primary-500'
                )} />
              </div>
              
              <div>
                <p className="text-lg font-medium text-secondary-900">
                  {isDragActive ? 'Suelta los archivos aquí' : 'Arrastra archivos aquí'}
                </p>
                <p className="text-secondary-600 mt-1">
                  o <span className="text-primary-600 font-medium">haz clic para seleccionar</span>
                </p>
              </div>
              
              <div className="text-sm text-secondary-500 space-y-1">
                <p>Formatos soportados: Excel (.xlsx, .xls), CSV, PDF, Word (.docx)</p>
                <p>Tamaño máximo: {isPremium ? '50MB' : '5MB'} por archivo</p>
                <p>Cantidad máxima: {isPremium ? '10' : '3'} archivos</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-secondary-900">
              Archivos Cargados ({uploadedFiles.length})
            </h2>
          </div>
          
          <div className="card-body p-0">
            <div className="space-y-1">
              {uploadedFiles.map((fileItem) => {
                const FileIcon = getFileIcon(fileItem.type);
                
                return (
                  <div key={fileItem.id} className="flex items-center p-4 hover:bg-secondary-50 transition-colors">
                    {/* File Icon */}
                    <div className="w-10 h-10 bg-secondary-100 rounded-lg flex items-center justify-center mr-4">
                      <FileIcon className="w-5 h-5 text-secondary-600" />
                    </div>
                    
                    {/* File Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <p className="font-medium text-secondary-900 truncate">
                          {fileItem.name}
                        </p>
                        <span className="text-sm text-secondary-500">
                          {formatFileSize(fileItem.size)}
                        </span>
                      </div>
                      
                      {/* Progress Bar */}
                      {fileItem.status === 'uploading' && (
                        <div className="mt-2">
                          <div className="flex items-center justify-between text-sm text-secondary-600 mb-1">
                            <span>Procesando...</span>
                            <span>{fileItem.progress}%</span>
                          </div>
                          <div className="w-full bg-secondary-200 rounded-full h-2">
                            <div 
                              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${fileItem.progress}%` }}
                            />
                          </div>
                        </div>
                      )}
                      
                      {/* Result Message */}
                      {fileItem.status === 'completed' && fileItem.result && (
                        <div className="mt-1">
                          <p className="text-sm text-success-600">
                            ✓ Procesado exitosamente - {fileItem.result.records_processed} registros
                          </p>
                        </div>
                      )}
                      
                      {fileItem.status === 'error' && (
                        <div className="mt-1">
                          <p className="text-sm text-error-600">
                            ✗ Error: {fileItem.result?.error || 'Error desconocido'}
                          </p>
                        </div>
                      )}
                    </div>
                    
                    {/* Status Icon */}
                    <div className="ml-4 flex items-center space-x-2">
                      {fileItem.status === 'uploading' && (
                        <Loader className="w-5 h-5 text-primary-600 animate-spin" />
                      )}
                      
                      {fileItem.status === 'completed' && (
                        <>
                          <button
                            onClick={() => viewPreview(fileItem)}
                            className="p-2 text-secondary-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                            title="Ver vista previa"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          
                          <button
                            onClick={() => downloadResult(fileItem)}
                            className="p-2 text-secondary-600 hover:text-success-600 hover:bg-success-50 rounded-lg transition-colors"
                            title="Descargar resultado"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          
                          <Check className="w-5 h-5 text-success-600" />
                        </>
                      )}
                      
                      {fileItem.status === 'error' && (
                        <AlertCircle className="w-5 h-5 text-error-600" />
                      )}
                      
                      {/* Remove Button */}
                      <button
                        onClick={() => removeFile(fileItem.id)}
                        className="p-2 text-secondary-400 hover:text-error-600 hover:bg-error-50 rounded-lg transition-colors"
                        title="Eliminar archivo"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="card p-6 bg-blue-50 border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-3">💡 Consejos para mejores resultados</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li>• Asegúrate de que tus archivos tengan headers (encabezados) en la primera fila</li>
          <li>• Los archivos Excel deben tener datos en la primera hoja</li>
          <li>• Para CSV, usa codificación UTF-8 para caracteres especiales</li>
          <li>• Los archivos PDF deben tener texto seleccionable (no imágenes escaneadas)</li>
          {isPremium && (
            <li>• Con tu cuenta Premium puedes usar IA para mejorar automáticamente tus datos</li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default FileUpload;
