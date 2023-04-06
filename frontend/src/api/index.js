import axios from 'axios';
import { getTokenFromLocalStorage } from '../lib/auth';

const apiClient = axios.create({
  baseURL: "/api",
  headers: {
    "Content-type": "application/json",
  },
}),
  getAuthConfig = () => ({  // TODO: user interceptors or similar
    headers: {
      Authorization: `Bearer ${getTokenFromLocalStorage()}`
    }
  });

export const api = {
  login: async (credentials) => {
    try {
      const response = await apiClient.post(`/auth/token/`, credentials, { headers: { "Content-type": 'application/x-www-form-urlencoded' } });
      return response.data.access_token;
    } catch (error) {
      return null
    }
  },

  isAuthenticated: async () => {
    const response = await apiClient.get(`/users/me/`, getAuthConfig())
    return response.data?.is_authenticated || false;
  },

  getEntriesList: async () => apiClient.get(`/entries/`, getAuthConfig()),

  getEntry: async (entry_id) => apiClient.get(`/entries/${entry_id}/`, getAuthConfig()),

  createEntry: async (file) => {
    let formData = new FormData();
    formData.append('payload', file)

    return apiClient.post(`/entries/`, formData, {
      headers: {
        "Content-type": 'multipart/form-data',
        ...getAuthConfig().headers,
      },
    })
  },

  getVisList: async (entryId) => apiClient.get(`/vis/?entry_id=${entryId}`, getAuthConfig()),

  getVis: async (visId) => apiClient.get(`/vis/${visId}/`, getAuthConfig()),

  getVisTypes: async (entryId) => apiClient.get(`/vis_types/`),

  createVis: async (entryId, visType, chartType, filters) => apiClient.post(`/vis/`, {
    entry_id: entryId,
    options: {
      vis_type: visType,
      chart_type: chartType,
      filters: filters,
    }
  }, getAuthConfig()),

};

export default api
