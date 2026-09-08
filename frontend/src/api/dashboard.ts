import { apiClient } from './client';
import { DashboardSummary } from '../types';

export const dashboardApi = {
  getSummary: async (): Promise<DashboardSummary> => {
    const res = await apiClient.get('/dashboard/summary/');
    return res.data;
  }
};
