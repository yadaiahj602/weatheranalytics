import { apiClient } from './client';
import { AlertRule, AlertEvent, IngestionJob } from '../types';

export const alertsApi = {
  getRules: async (): Promise<AlertRule[]> => {
    const res = await apiClient.get('/alerts/rules/');
    return res.data.results || res.data;
  },

  getEvents: async (): Promise<AlertEvent[]> => {
    const res = await apiClient.get('/alerts/events/');
    return res.data.results || res.data;
  },

  createRule: async (data: Partial<AlertRule>): Promise<AlertRule> => {
    const res = await apiClient.post('/alerts/rules/', data);
    return res.data;
  },

  getIngestionJobs: async (): Promise<IngestionJob[]> => {
    const res = await apiClient.get('/ingestion/jobs/');
    return res.data.results || res.data;
  },

  triggerIngestion: async (source = 'open_meteo'): Promise<any> => {
    const res = await apiClient.post('/ingestion/jobs/trigger/', { source });
    return res.data;
  }
};
