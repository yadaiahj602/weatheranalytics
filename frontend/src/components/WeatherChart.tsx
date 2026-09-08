import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Bar,
  ComposedChart,
  Line,
  Legend
} from 'recharts';
import { WeatherReading } from '../types';

interface WeatherChartProps {
  readings: WeatherReading[];
  stationName?: string;
  hours?: number;
  onHoursChange?: (hours: number) => void;
}

export const WeatherChart: React.FC<WeatherChartProps> = ({
  readings,
  stationName = 'Station Observations',
  hours = 24,
  onHoursChange,
}) => {
  const chartData = readings.map((r) => {
    const d = new Date(r.timestamp);
    const timeLabel = `${d.getUTCHours().toString().padStart(2, '0')}:00 UTC`;
    return {
      time: timeLabel,
      fullTime: d.toUTCString(),
      temperature: r.temperature_c !== null ? Number(r.temperature_c.toFixed(1)) : null,
      humidity: r.humidity_pct !== null ? Number(r.humidity_pct.toFixed(0)) : null,
      pressure: r.pressure_hpa !== null ? Number(r.pressure_hpa.toFixed(0)) : null,
      windSpeed: r.wind_speed_ms !== null ? Number(r.wind_speed_ms.toFixed(1)) : null,
      precipitation: r.precipitation_mm !== null ? Number(r.precipitation_mm.toFixed(1)) : 0,
    };
  });

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-md">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <span>{stationName}</span>
            <span className="rounded-md bg-blue-500/10 px-2 py-0.5 text-xs text-blue-400 border border-blue-500/20">
              {readings.length} data points
            </span>
          </h3>
          <p className="text-xs text-slate-400">Chronological meteorological readings</p>
        </div>

        {onHoursChange && (
          <div className="flex items-center space-x-1 rounded-xl bg-slate-800/80 p-1 border border-slate-700/60 text-xs">
            {[12, 24, 48, 72].map((h) => (
              <button
                key={h}
                onClick={() => onHoursChange(h)}
                className={`rounded-lg px-3 py-1 font-semibold transition-all ${
                  hours === h
                    ? 'bg-cyan-500 text-white shadow-sm shadow-cyan-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {h}h
              </button>
            ))}
          </div>
        )}
      </div>

      {readings.length === 0 ? (
        <div className="flex h-64 items-center justify-center text-xs text-slate-400 italic">
          No observation data available for this range. Click "Sync Weather Now" to ingest data.
        </div>
      ) : (
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis yAxisId="temp" stroke="#06b6d4" fontSize={11} tickLine={false} domain={['dataMin - 2', 'dataMax + 2']} />
              <YAxis yAxisId="humidity" orientation="right" stroke="#818cf8" fontSize={11} tickLine={false} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '0.75rem',
                  fontSize: '12px',
                  boxShadow: '0 10px 15px -3px rgba(0,0,0,0.5)',
                }}
                labelStyle={{ color: '#94a3b8', fontWeight: 'bold' }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
              <Area
                yAxisId="temp"
                type="monotone"
                dataKey="temperature"
                name="Temperature (°C)"
                stroke="#06b6d4"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#tempGradient)"
              />
              <Line
                yAxisId="humidity"
                type="monotone"
                dataKey="humidity"
                name="Humidity (%)"
                stroke="#818cf8"
                strokeWidth={2}
                dot={false}
              />
              <Bar
                yAxisId="temp"
                dataKey="precipitation"
                name="Precip (mm)"
                fill="#38bdf8"
                barSize={6}
                radius={[4, 4, 0, 0]}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};
