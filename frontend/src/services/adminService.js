import api from './api';

export const adminService = {
  async getSettings() {
    const r = await api.get('/api/admin/settings');
    return r.data;
  },
  async setSetting(payload) {
    const body = {
      provider: payload.provider,
      api_key: payload.api_key,
      notes: payload.notes || ''
    };
    const r = await api.post('/api/admin/settings', body);
    return r.data;
  },
  async deleteSetting(provider) {
    const r = await api.delete(`/api/admin/settings/${encodeURIComponent(provider)}`);
    return r.data;
  }
};

export default adminService;
