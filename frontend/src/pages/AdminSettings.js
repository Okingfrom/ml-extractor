import React, { useState, useEffect } from 'react';
import { adminService } from '../services/adminService';

export default function AdminSettings() {
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState({});
  const [provider, setProvider] = useState('mercadolibre');
  const [apiKey, setApiKey] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const res = await adminService.getSettings();
        setSettings(res.settings || {});
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

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
