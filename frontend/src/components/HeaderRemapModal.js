import React, { useState } from 'react';

const LOGICAL_FIELDS = [
  'title','price','stock','sku','images','description','condition','shipping','category','brand','model','weight','dimensions','warranty'
];

export default function HeaderRemapModal({ open, unknownHeaders = [], onClose, onApply }) {
  const [mappings, setMappings] = useState(() => {
    const initial = {};
    unknownHeaders.forEach(h => { initial[h] = ''; });
    return initial;
  });

  // optional sample rows will be shown when provided via prop (not required for API)


  React.useEffect(() => {
    // reset when unknownHeaders change
    const initial = {};
    unknownHeaders.forEach(h => { initial[h] = ''; });
    setMappings(initial);
  }, [unknownHeaders]);

  const handleChange = (hdr, val) => {
    setMappings(prev => ({ ...prev, [hdr]: val }));
  };

  const handleApply = () => {
    // require at least one mapping to be set before applying
    const selected = Object.values(mappings).filter(v => v && LOGICAL_FIELDS.includes(v));
    if (selected.length === 0) {
      // nothing selected
      return;
    }
    onApply(mappings);
    onClose();
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl p-6">
        <h3 className="text-lg font-semibold mb-3">Remapear encabezados desconocidos</h3>
        <p className="text-sm text-gray-600 mb-4">Algunos encabezados no se pudieron mapear automáticamente. Selecciona a qué campo lógico deben mapearse o déjalos en blanco para ignorarlos.</p>

        <div className="space-y-3 max-h-60 overflow-auto">
          {unknownHeaders.map((h) => (
            <div key={h} className="flex items-center space-x-3">
              <div className="flex-1 font-mono text-sm text-gray-800">{h}</div>
              <select
                value={mappings[h] || ''}
                onChange={(e) => handleChange(h, e.target.value)}
                className="border rounded p-2"
              >
                <option value="">-- Ignorar --</option>
                {LOGICAL_FIELDS.map(f => (
                  <option key={f} value={f}>{f}</option>
                ))}
              </select>
            </div>
          ))}
        </div>
        <div className="mt-3 text-xs text-gray-500">Consejo: puedes mapear solo los encabezados necesarios; los no mapeados serán ignorados.</div>

        <div className="mt-6 flex justify-end space-x-3">
          <button onClick={onClose} className="px-4 py-2 rounded border">Cancelar</button>
          <button
            onClick={handleApply}
            disabled={Object.values(mappings).filter(v => v && LOGICAL_FIELDS.includes(v)).length === 0}
            className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-50"
          >Aplicar</button>
        </div>
      </div>
    </div>
  );
}
