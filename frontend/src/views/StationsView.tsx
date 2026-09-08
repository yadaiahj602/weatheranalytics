import React, { useState, useEffect } from 'react';
import { WeatherStation, WeatherReading } from '../types';
import { weatherApi } from '../api/weather';
import { WeatherChart } from '../components/WeatherChart';
import {
  Compass,
  MapPin,
  Mountain,
  Thermometer,
  Droplets,
  Wind,
  Gauge,
  Calendar,
  Cpu,
  RefreshCw
} from 'lucide-react';

interface StationsViewProps {
  stations: WeatherStation[];
  selectedStation: WeatherStation | null;
  onSelectStation: (station: WeatherStation) => void;
  onNavigateToPredict: (station: WeatherStation) => void;
}

export const StationsView: React.FC<StationsViewProps> = ({
  stations,
  selectedStation,
  onSelectStation,
  onNavigateToPredict,
}) => {
  const [readings, setReadings] = useState<WeatherReading[]>([]);
  const [hours, setHours] = useState(24);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const activeStation = selectedStation || stations[0];

  useEffect(() => {
    if (activeStation) {
      loadHistory(activeStation.id, hours);
    }
  }, [activeStation?.id, hours]);

  const loadHistory = async (stationId: number, h: number) => {
    try {
      setLoadingHistory(true);
      const data = await weatherApi.getStationHistory(stationId, h);
      setReadings(data.readings || []);
      setLoadingHistory(false);
    } catch (e) {
      console.error(e);
      setLoadingHistory(false);
    }
  };

  const filteredStations = stations.filter(
    (s) =>
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Station Selector & Search */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
            <Compass className="h-6 w-6 text-cyan-400" />
            <span>Weather Stations & Live Telemetry</span>
          </h2>
          <p className="text-xs text-slate-400">
            Select a station to inspect physical parameters and historical curves
          </p>
        </div>

        <input
          type="text"
          placeholder="Search by station code or city..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full sm:w-64 rounded-xl border border-slate-800 bg-slate-900 px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
        />
      </div>

      {/* Station Pills Carousel / Horizontal Scroll */}
      <div className="flex space-x-3 overflow-x-auto pb-2">
        {filteredStations.map((station) => {
          const isSelected = activeStation?.id === station.id;
          return (
            <button
              key={station.id}
              onClick={() => onSelectStation(station)}
              className={`flex-shrink-0 rounded-xl border p-3 text-left transition-all min-w-[170px] ${
                isSelected
                  ? 'border-cyan-500 bg-cyan-500/10 shadow-lg shadow-cyan-500/10'
                  : 'border-slate-800 bg-slate-900/60 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-cyan-400">{station.code}</span>
                <span className="text-xs font-extrabold text-white">
                  {station.latest_reading?.temperature_c !== null && station.latest_reading?.temperature_c !== undefined
                    ? `${station.latest_reading.temperature_c}°C`
                    : '--'}
                </span>
              </div>
              <div className="text-xs font-medium text-slate-200 mt-1 truncate">{station.name}</div>
            </button>
          );
        })}
      </div>

      {/* Detailed View for Active Station */}
      {activeStation && (
        <div className="space-y-6">
          {/* Station Metadata Banner */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-md">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="rounded-lg bg-cyan-500/20 px-2.5 py-1 font-mono text-xs font-bold text-cyan-400 border border-cyan-500/30">
                    {activeStation.code}
                  </span>
                  <h3 className="text-lg font-bold text-white">{activeStation.name}</h3>
                </div>
                <div className="mt-2 flex flex-wrap items-center gap-4 text-xs text-slate-400">
                  <span className="flex items-center gap-1">
                    <MapPin className="h-3.5 w-3.5 text-slate-500" />
                    {activeStation.latitude?.toFixed(4)}, {activeStation.longitude?.toFixed(4)}
                  </span>
                  <span className="flex items-center gap-1">
                    <Mountain className="h-3.5 w-3.5 text-slate-500" />
                    {activeStation.elevation_m} m elevation
                  </span>
                  <span className="text-emerald-400 font-semibold">● Operational</span>
                </div>
              </div>

              <button
                onClick={() => onNavigateToPredict(activeStation)}
                className="flex items-center space-x-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-4 py-2.5 text-xs font-bold text-white shadow-lg shadow-purple-600/20 hover:from-purple-500 hover:to-indigo-500 transition-all"
              >
                <Cpu className="h-4 w-4" />
                <span>Run ML 24h Prediction</span>
              </button>
            </div>
          </div>

          {/* Time Series Chart */}
          <WeatherChart
            readings={readings}
            stationName={`${activeStation.name} (${activeStation.code})`}
            hours={hours}
            onHoursChange={setHours}
          />

          {/* Readings History Table */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-md">
            <h4 className="text-sm font-bold text-white mb-3">Recent Historical Observations</h4>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-500">
                  <tr>
                    <th className="py-2.5 px-3">Timestamp (UTC)</th>
                    <th className="py-2.5 px-3">Air Temp</th>
                    <th className="py-2.5 px-3">Humidity</th>
                    <th className="py-2.5 px-3">Pressure</th>
                    <th className="py-2.5 px-3">Wind Speed</th>
                    <th className="py-2.5 px-3">Wind Direction</th>
                    <th className="py-2.5 px-3">Precipitation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {readings.slice(0, 15).map((r) => (
                    <tr key={r.id} className="hover:bg-slate-800/30">
                      <td className="py-2.5 px-3 font-mono text-slate-400">
                        {new Date(r.timestamp).toUTCString()}
                      </td>
                      <td className="py-2.5 px-3 font-semibold text-rose-400">
                        {r.temperature_c !== null ? `${r.temperature_c}°C` : '--'}
                      </td>
                      <td className="py-2.5 px-3 text-cyan-400">
                        {r.humidity_pct !== null ? `${r.humidity_pct}%` : '--'}
                      </td>
                      <td className="py-2.5 px-3 text-purple-400">
                        {r.pressure_hpa !== null ? `${r.pressure_hpa} hPa` : '--'}
                      </td>
                      <td className="py-2.5 px-3 text-amber-400">
                        {r.wind_speed_ms !== null ? `${r.wind_speed_ms} m/s` : '--'}
                      </td>
                      <td className="py-2.5 px-3 text-slate-400">
                        {r.wind_direction_deg !== null ? `${r.wind_direction_deg}°` : '--'}
                      </td>
                      <td className="py-2.5 px-3 text-blue-400">
                        {r.precipitation_mm !== null ? `${r.precipitation_mm} mm` : '0 mm'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
