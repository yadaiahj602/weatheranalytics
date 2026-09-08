import { apiClient } from './client';
import { Incident } from '../types';

export const incidentsApi = {
  getIncidents: async (params?: Record<string, any>): Promise<Incident[]> => {
    const res = await apiClient.get('/incidents/incidents/', { params });
    return res.data.results || res.data;
  },

  getIncidentsGeoJSON: async (status?: string): Promise<any> => {
    const res = await apiClient.get('/incidents/incidents/geojson/', {
      params: status ? { status } : {},
    });
    return res.data;
  },

  createIncident: async (formData: FormData): Promise<Incident> => {
    const res = await apiClient.post('/incidents/incidents/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  updateIncidentStatus: async (id: number, status: string): Promise<Incident> => {
    const res = await apiClient.patch(`/incidents/incidents/${id}/`, { status });
    return res.data;
  },

  deleteIncident: async (id: number): Promise<void> => {
    await apiClient.delete(`/incidents/incidents/${id}/`);
  }
};
