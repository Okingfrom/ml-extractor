import React, { useState, useEffect } from 'react';
import { adminService } from '../services/adminService';
import { logger } from '../utils/logger';

export default function AdminSettings() {
  // Initialize all hooks first (before any early returns)
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState({});
  const [provider, setProvider] = useState('mercadolibre');
  const [apiKey, setApiKey] = useState('');
  const [notes, setNotes] = useState('');

  // Basic role check: ensure frontend user is admin before loading settings
  const currentUser = JSON.parse(localStorage.getItem('user') || 'null');
  const isAdmin = currentUser && currentUser.role === 'admin';

  useEffect(() => {
    if (!isAdmin) {
      setLoading(false);
      return;
    }
    
    async function load() {
      try {
        const res = await adminService.getSettings();
        setSettings(res.settings || {});
      } catch (e) {
        logger.error('Error loading admin settings:', e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [isAdmin]);

  if (!isAdmin) {
    return (<div>Acceso denegado: necesita permisos de administrador.</div>);
  }

  const save = async () => {
    await adminService.setSetting({ provider, api_key: apiKey, notes });
    const res = await adminService.getSettings();
    setSettings(res.settings || {});
    setApiKey('');
    setNotes('');
  };

  const remove = async (p) => {
    await adminService.deleteSetting(p);
    const res = await adminService.getSettings();
    setSettings(res.settings || {});
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="admin-settings">
      <h2>Admin Settings</h2>
      <div>
        <label>Provider</label>
        <input value={provider} onChange={e => setProvider(e.target.value)} />
      </div>
      <div>
        <label>API Key</label>
        <input value={apiKey} onChange={e => setApiKey(e.target.value)} />
      </div>
      <div>
        <label>Notes</label>
        <input value={notes} onChange={e => setNotes(e.target.value)} />
      </div>
      <button onClick={save}>Guardar</button>

      <h3>Stored Keys</h3>
      <ul>
        {Object.keys(settings).map(k => (
          <li key={k}>
            <strong>{k}</strong>: {settings[k].api_key_masked} {settings[k].notes}
            <button onClick={() => remove(k)}>Eliminar</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
