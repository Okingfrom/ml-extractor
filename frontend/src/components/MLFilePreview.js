import React, { useState, useEffect, useCallback } from 'react';
import { mapHeaderToLogical } from '../utils/headerMapper';
import LoadingSpinner from './LoadingSpinner';
import toast from 'react-hot-toast';
import HeaderRemapModal from './HeaderRemapModal';

const MLFilePreview = ({ 
  mlTemplate, 
  productData, 
  mappingConfig, 
  defaultSettings, 
  onPreviewGenerated,
  onGenerateFile
}) => {
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [editingCell, setEditingCell] = useState(null); // { row: number, header: string }
  const [cellInputValue, setCellInputValue] = useState('');
  const [editsMap, setEditsMap] = useState({}); // key: `${row}|${header}` -> value
  const [applyingEdits, setApplyingEdits] = useState(false);
  const [showRemapModal, setShowRemapModal] = useState(false);
  const [unknownHeadersForRemap, setUnknownHeadersForRemap] = useState([]);
  const [pendingInvalidEdits, setPendingInvalidEdits] = useState([]);

  useEffect(() => {
    generatePreview();
  }, [mlTemplate, productData, mappingConfig, defaultSettings]);

  const generatePreview = async () => {
    if (!mlTemplate || !productData || !mappingConfig) return;

    setLoading(true);
    setError(null);

    try {
      const fileService = await import('../services/fileService');
      const result = await fileService.default.generateMLFilePreview(
        mlTemplate,
        productData,
        mappingConfig,
        defaultSettings
      );

      setPreview(result.preview);
      if (onPreviewGenerated) {
        onPreviewGenerated(result);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error generando vista previa');
      console.error('Preview error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateFile = () => {
    if (onGenerateFile) {
      onGenerateFile();
    }
  };

  const startEditCell = (row, header, currentValue) => {
    setEditingCell({ row, header });
    setCellInputValue(currentValue || '');
  };

  const saveEditCell = () => {
    if (!editingCell) return;
    const key = `${editingCell.row}|${editingCell.header}`;
    setEditsMap(prev => ({ ...prev, [key]: cellInputValue }));
    setEditingCell(null);
    setCellInputValue('');
    toast.success('Edición guardada localmente');
  };

  const cancelEditCell = () => {
    setEditingCell(null);
    setCellInputValue('');
  };

  const applyEdits = async () => {
    if (!mlTemplate || !productData) {
      toast.error('Faltan archivos: plantilla o datos de productos');
      return;
    }

    // Map preview header -> logical field expected by backend (title, price, stock, ...)
  // use shared mapper

    const editsPayload = [];
    const invalidHeaders = [];
    Object.entries(editsMap).forEach(([k, v]) => {
      const [rowStr, header] = k.split('|');
      const row = parseInt(rowStr, 10);
      const logical = mapHeaderToLogical(header);
      if (!logical) {
        invalidHeaders.push(header);
        return;
      }
      editsPayload.push({ row: row, field: logical, value: v });
    });

    if (editsPayload.length === 0) {
      if (invalidHeaders.length > 0) {
        // Open remap modal to let user choose mappings for unknown headers
        const uniq = [...new Set(invalidHeaders)];
        setUnknownHeadersForRemap(uniq);
        // capture the invalid edit keys so we can retry after remap
        setPendingInvalidEdits(Object.entries(editsMap).filter(([k]) => {
          const header = k.split('|')[1];
          return uniq.includes(header);
        }));
        setShowRemapModal(true);
      } else {
        toast('No hay ediciones para aplicar');
      }
      return;
    }

    setApplyingEdits(true);
    try {
      const fileService = await import('../services/fileService');
      const result = await fileService.default.generateMLFile(
        mlTemplate,
        productData,
        mappingConfig,
        defaultSettings || {},
        null,
        'interactive',
        editsPayload
      );

      if (result && result.download && result.download.filename) {
        // trigger download
        await fileService.default.downloadMLFile(result.download.filename);
        toast.success('Ediciones aplicadas y archivo descargado');
      } else if (result && result.download && result.download.url) {
        // fallback: navigate to download url
        window.location.href = result.download.url;
        toast.success('Ediciones aplicadas, iniciando descarga');
      } else {
        toast.success('Ediciones aplicadas');
      }

      // Clear local edits after successful apply
      setEditsMap({});
    } catch (err) {
      console.error('Apply edits error:', err);
      toast.error(err.response?.data?.detail || 'Error aplicando ediciones');
    } finally {
      setApplyingEdits(false);
    }
  };

  const handleRemapApply = async (mappings) => {
    // mappings: { originalHeader: logicalField }
    // convert pendingInvalidEdits using mappings and then call backend
    const extraPayload = [];
    pendingInvalidEdits.forEach(([k, v]) => {
      const [rowStr, header] = k.split('|');
      const row = parseInt(rowStr, 10);
      const logical = mappings[header];
      if (logical) {
        extraPayload.push({ row, field: logical, value: v });
      }
    });

    if (extraPayload.length === 0) {
      toast.error('No se remapearon encabezados válidos');
      return;
    }

    // Combine with already-mapped edits
    const existingPayload = [];
    Object.entries(editsMap).forEach(([k, v]) => {
      const [rowStr, header] = k.split('|');
      const row = parseInt(rowStr, 10);
      const logical = mapHeaderToLogical(header);
      if (logical) existingPayload.push({ row, field: logical, value: v });
    });

    const finalPayload = existingPayload.concat(extraPayload);

    // send to backend
    setApplyingEdits(true);
    try {
      const fileService = await import('../services/fileService');
      const result = await fileService.default.generateMLFile(
        mlTemplate,
        productData,
        mappingConfig,
        defaultSettings || {},
        null,
        'interactive',
        finalPayload
      );

      if (result && result.download && result.download.filename) {
        await fileService.default.downloadMLFile(result.download.filename);
        toast.success('Ediciones aplicadas y archivo descargado');
      } else if (result && result.download && result.download.url) {
        window.location.href = result.download.url;
        toast.success('Ediciones aplicadas, iniciando descarga');
      } else {
        toast.success('Ediciones aplicadas');
      }

      // Remove applied edits from local map
      const newEdits = { ...editsMap };
      extraPayload.forEach(ep => {
        const key = `${ep.row}|${Object.keys(mappings).find(k => mappings[k] === ep.field)}`;
        delete newEdits[key];
      });
      setEditsMap(newEdits);
      setPendingInvalidEdits([]);
    } catch (err) {
      console.error('Remap apply error:', err);
      toast.error('Error aplicando ediciones remapeadas');
    } finally {
      setApplyingEdits(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          🔍 Generando Vista Previa...
        </h3>
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          🔍 Vista Previa del Archivo Final
        </h3>
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-red-400">❌</span>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Error en Vista Previa
              </h3>
              <div className="mt-2 text-sm text-red-700">
                {error}
              </div>
            </div>
          </div>
          <div className="mt-4">
            <button
              onClick={generatePreview}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              🔄 Reintentar Vista Previa
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!preview) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          🔍 Vista Previa del Archivo Final
        </h3>
        <p className="text-gray-500">
          Esperando datos para generar vista previa...
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          🔍 Vista Previa del Archivo Final
        </h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleGenerateFile}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            ⬇️ Descargar Archivo Completo
          </button>
          <button
            onClick={() => {
              // open remap for all unknown headers
              const unknowns = preview.headers.filter(h => !mapHeaderToLogical(h));
              if (unknowns.length === 0) {
                toast('No hay encabezados desconocidos para remapear');
                return;
              }
              setUnknownHeadersForRemap(unknowns);
              setPendingInvalidEdits([]);
              setShowRemapModal(true);
            }}
            className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md bg-white hover:bg-gray-50"
          >Remapear Encabezados</button>
        </div>
      </div>

      {/* Summary Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-sm font-medium text-blue-900">Total Productos</div>
          <div className="text-2xl font-bold text-blue-600">{preview.total_products}</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-sm font-medium text-green-900">Vista Previa</div>
          <div className="text-2xl font-bold text-green-600">{preview.preview_count} filas</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-sm font-medium text-purple-900">Campos Mapeados</div>
          <div className="text-2xl font-bold text-purple-600">{Object.keys(mappingConfig).length}</div>
        </div>
      </div>

      {/* Preview Table */}
      <div className="overflow-x-auto">
        <div className="mb-4">
          <p className="text-sm text-gray-600">
            📋 Mostrando las primeras {preview.preview_count} filas de {preview.total_products} productos
          </p>
        </div>
        
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                #
              </th>
              {preview.headers.slice(0, 8).map((header, index) => {
                const logical = mapHeaderToLogical(header);
                return (
                  <th
                    key={index}
                    className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    <div className="flex items-center space-x-2">
                      <span>{header}</span>
                      {!logical && (
                        <button
                          title="Remapear este encabezado"
                          onClick={() => {
                            setUnknownHeadersForRemap([header]);
                            setPendingInvalidEdits([]);
                            setShowRemapModal(true);
                          }}
                          className="text-xs text-yellow-700 bg-yellow-100 px-2 py-1 rounded"
                        >Remap</button>
                      )}
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
                {preview.rows.map((row, rowIndex) => (
              <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {row.row_number}
                </td>
                {preview.headers.slice(0, 8).map((header, colIndex) => {
                  const currentValue = row.mapped_data[header] || '';
                  const editKey = `${row.row_number}|${header}`;
                  const stagedValue = editsMap[editKey];
                  return (
                    <td
                      key={colIndex}
                      className="px-3 py-4 whitespace-nowrap text-sm text-gray-900"
                    >
                      {editingCell && editingCell.row === row.row_number && editingCell.header === header ? (
                        <div className="flex items-center space-x-2">
                          <input
                            autoFocus
                            value={cellInputValue}
                            onChange={(e) => setCellInputValue(e.target.value)}
                            onKeyDown={(e) => { if (e.key === 'Enter') saveEditCell(); if (e.key === 'Escape') cancelEditCell(); }}
                            className="border rounded px-2 py-1 w-full"
                          />
                          <button onClick={saveEditCell} className="text-sm text-green-600">Guardar</button>
                          <button onClick={cancelEditCell} className="text-sm text-gray-500">Cancelar</button>
                        </div>
                      ) : (
                        <div
                          className="max-w-32 truncate cursor-pointer"
                          title={(stagedValue ?? currentValue) || ''}
                          onClick={() => startEditCell(row.row_number, header, stagedValue ?? currentValue)}
                        >
                          {stagedValue !== undefined ? (
                            <span className="text-blue-700">{stagedValue}</span>
                          ) : (
                            (currentValue && currentValue !== '') ? currentValue : '-'
                          )}
                        </div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Show more columns if available */}
      {preview.headers.length > 8 && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
          <p className="text-sm text-yellow-800">
            ℹ️ Hay {preview.headers.length - 8} columnas adicionales que se incluirán en el archivo final.
          </p>
        </div>
      )}

      {/* Mapping Details */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Applied Mappings */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="text-sm font-medium text-gray-900 mb-3">🗺️ Mapeos Aplicados</h4>
          <div className="space-y-2">
            {Object.entries(mappingConfig).map(([mlField, productField], index) => (
              <div key={index} className="flex justify-between text-xs">
                <span className="text-gray-600 truncate">{mlField}:</span>
                <span className="text-gray-900 truncate ml-2">{productField}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Default Settings */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="text-sm font-medium text-gray-900 mb-3">⚙️ Configuración por Defecto</h4>
          <div className="space-y-2">
            {Object.entries(defaultSettings).map(([key, value], index) => (
              <div key={index} className="flex justify-between text-xs">
                <span className="text-gray-600 truncate">{key}:</span>
                <span className="text-gray-900 truncate ml-2">{value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex flex-col sm:flex-row gap-3">
        <button
          onClick={generatePreview}
          className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          🔄 Actualizar Vista Previa
        </button>
        
        <button
          onClick={handleGenerateFile}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          📤 Generar y Descargar Archivo Final
        </button>
        {/* Edits panel */}
        <div className="ml-0 sm:ml-4 mt-3 sm:mt-0">
          <div className="text-sm text-gray-600 mb-2">Ediciones locales: {Object.keys(editsMap).length}</div>
          <div className="flex items-center gap-2">
            <button
              onClick={applyEdits}
              disabled={applyingEdits || Object.keys(editsMap).length === 0}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-500 hover:bg-blue-600 disabled:opacity-50"
            >
              {applyingEdits ? 'Aplicando...' : 'Aplicar Edits (interactive)'}
            </button>
            <button
              onClick={() => setEditsMap({})}
              disabled={Object.keys(editsMap).length === 0}
              className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md bg-white hover:bg-gray-50"
            >
              Limpiar Edits
            </button>
          </div>
        </div>
      </div>
      <HeaderRemapModal
        open={showRemapModal}
        unknownHeaders={unknownHeadersForRemap}
        onClose={() => setShowRemapModal(false)}
        onApply={handleRemapApply}
      />
    </div>
  );
};

export default MLFilePreview;
