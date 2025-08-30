import React from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const DebugPanel = () => {
  const { lastError } = useAuth();
  const token = localStorage.getItem('token');
  const user = localStorage.getItem('user');

  return (
    <div style={{position: 'fixed', right: 10, bottom: 10, background: 'rgba(0,0,0,0.8)', color: '#fff', padding: 12, borderRadius: 8, zIndex: 9999, maxWidth: 420}}>
      <h4 style={{margin: 0, marginBottom: 8}}>Debug Panel (dev only)</h4>
      <div style={{fontSize: 12, marginBottom: 6}}><strong>Token:</strong> {token ? token.substring(0,20) + '...' : 'none'}</div>
      <div style={{fontSize: 12, marginBottom: 6}}><strong>User (localStorage):</strong> {user || 'none'}</div>
      <div style={{fontSize: 12}}><strong>Last Error:</strong> {lastError ? JSON.stringify(lastError) : 'none'}</div>
      <div style={{marginTop: 8}}>
        <button
          onClick={async () => {
            try {
              const payload = { source: 'frontend-debug-panel', payload: { token: token || null, user: user ? JSON.parse(user) : null, lastError } };
              await api.post('/api/debug/logs', payload);
              alert('Logs sent to backend/logs/debug-logs.json');
            } catch (err) {
              alert('Failed to send logs: ' + (err?.message || err));
            }
          }}
          style={{background: '#1f2937', color: '#fff', padding: '6px 8px', borderRadius: 4, border: 'none', cursor: 'pointer'}}
        >Send logs to backend</button>
      </div>
    </div>
  );
};

export default DebugPanel;
