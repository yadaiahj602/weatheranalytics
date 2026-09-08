import { apiClient } from './client';
import { WeatherStation, WeatherReading, PredictionResult } from '../types';

export const weatherApi = {
  getStations: async (): Promise<WeatherStation[]> => {
    const res = await apiClient.get('/weather/stations/');
    return res.data.results || res.data;
  },

  getStationGeoJSON: async (): Promise<any> => {
    const res = await apiClient.get('/weather/stations/geojson/');
    return res.data;
  },

  getStationHistory: async (stationId: number, hours = 24): Promise<{ count: number; readings: WeatherReading[] }> => {
    const res = await apiClient.get(`/weather/stations/${stationId}/history/?hours=${hours}`);
    return res.data;
  },

  getReadings: async (params?: Record<string, any>): Promise<WeatherReading[]> => {
    const res = await apiClient.get('/weather/readings/', { params });
    return res.data.results || res.data;
  },

  getStationPrediction: async (stationId: number): Promise<PredictionResult> => {
    const res = await apiClient.get(`/weather/stations/${stationId}/predict/`);
    return res.data;
  },

  getAllPredictions: async (): Promise<PredictionResult[]> => {
    const res = await apiClient.get('/weather/stations/predictions/');
    return res.data;
  },

  createStation: async (data: Partial<WeatherStation>): Promise<WeatherStation> => {
    const res = await apiClient.post('/weather/stations/', data);
    return res.data;
  }
};
