export interface WeatherStation {
  id: number;
  code: string;
  name: string;
  latitude: number | null;
  longitude: number | null;
  elevation_m: number | null;
  is_active: boolean;
  latest_reading?: {
    timestamp: string;
    temperature_c: number | null;
    humidity_pct: number | null;
    pressure_hpa: number | null;
    wind_speed_ms: number | null;
    precipitation_mm: number | null;
  } | null;
  created_at: string;
  updated_at: string;
}

export interface WeatherReading {
  id: number;
  station: number;
  station_code: string;
  station_name: string;
  timestamp: string;
  temperature_c: number | null;
  humidity_pct: number | null;
  pressure_hpa: number | null;
  wind_speed_ms: number | null;
  wind_direction_deg: number | null;
  precipitation_mm: number | null;
  cloud_cover_pct: number | null;
  visibility_m: number | null;
  created_at: string;
}

export interface Incident {
  id: number;
  title: string;
  description: string;
  incident_type: 'flood' | 'storm' | 'heatwave' | 'drought' | 'tornado' | 'blizzard' | 'other';
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'monitoring' | 'resolved' | 'closed';
  is_active: boolean;
  affected_area?: any;
  centroid?: { latitude: number; longitude: number } | null;
  image?: string | null;
  start_time: string;
  end_time?: string | null;
  reported_by?: number | null;
  reported_by_username?: string;
  created_at: string;
  updated_at: string;
}

export interface AlertRule {
  id: number;
  name: string;
  description: string;
  condition_type: string;
  threshold: number;
  station?: number | null;
  station_name?: string;
  channel: string;
  recipients: string[];
  is_active: boolean;
  created_at: string;
}

export interface AlertEvent {
  id: number;
  rule: number;
  rule_name: string;
  condition_type: string;
  threshold: number;
  station_name: string;
  triggered_at: string;
  notify_status: 'pending' | 'sent' | 'failed';
  notify_sent_at?: string | null;
  error_message?: string;
}

export interface IngestionJob {
  id: number;
  source: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  started_at: string | null;
  finished_at: string | null;
  records_processed: number;
  error_message: string;
  created_at: string;
}

export interface HourlyForecast {
  forecast_hour: number;
  timestamp: string;
  predicted_temp_c: number;
  predicted_humidity_pct: number;
  predicted_pressure_hpa: number;
  predicted_wind_ms: number;
  precipitation_probability_pct: number;
  estimated_precipitation_mm: number;
  confidence_score: number;
}

export interface PredictionResult {
  station_id: number;
  station_code: string;
  station_name: string;
  generated_at: string;
  model_architecture: string;
  model_trained_on_history: boolean;
  sample_size: number;
  feature_importance: Record<string, number>;
  summary_24h: {
    max_temp_c: number;
    min_temp_c: number;
    expected_precip_mm: number;
    max_wind_speed_ms: number;
  };
  hazard_risks: {
    heatwave: 'Low' | 'Moderate' | 'High';
    storm_squall: 'Low' | 'Moderate' | 'High';
    freeze: 'Low' | 'Moderate' | 'High';
    flash_flood: 'Low' | 'Moderate' | 'High';
  };
  forecast: HourlyForecast[];
}

export interface DashboardSummary {
  generated_at: string;
  stations: {
    total: number;
    active: number;
  };
  observations_last_24h: {
    count: number;
    avg_temp: number | null;
    max_temp: number | null;
    min_temp: number | null;
    avg_humidity: number | null;
    total_precip: number | null;
  };
  active_incidents: {
    total_active: number;
    critical: number;
    high: number;
  };
  alert_events_last_24h: {
    total: number;
    pending: number;
    sent: number;
    failed: number;
  };
  active_alert_rules: number;
}
