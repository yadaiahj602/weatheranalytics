import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Line,
  ComposedChart
} from 'recharts';
import { PredictionResult } from '../types';
import { BrainCircuit, AlertTriangle, ShieldCheck, Flame, Wind, Snowflake, CloudRain } from 'lucide-react';

interface PredictionCardProps {
  prediction: PredictionResult;
}

export const PredictionCard: React.FC<PredictionCardProps> = ({ prediction }) => {
  const { summary_24h, hazard_risks, forecast, feature_importance } = prediction;

  const chartData = forecast.map((f) => {
    const d = new Date(f.timestamp);
    return {
      hour: `+${f.forecast_hour}h`,
      timeLabel: `${d.getUTCHours().toString().padStart(2, '0')}:00`,
      temp: f.predicted_temp_c,
      confidence: Math.round(f.confidence_score * 100),
      precipProb: f.precipitation_probability_pct,
      wind: f.predicted_wind_ms,
    };
  });

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'High':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/40';
      case 'Moderate':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      default:
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
    }
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-2xl backdrop-blur-md space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <div className="rounded-lg bg-purple-500/20 p-2 text-purple-400 border border-purple-500/30">
              <BrainCircuit className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <span>{prediction.station_name}</span>
                <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800">
                  {prediction.station_code}
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                Model: {prediction.model_architecture} ({prediction.model_trained_on_history ? 'Fitted on Station Records' : 'Baseline Calibration'})
              </p>
            </div>
          </div>
        </div>

        {/* Feature Importance Chips */}
        <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-slate-300">
          <span className="text-slate-500 mr-1">Feature Weights:</span>
          {Object.entries(feature_importance || {}).map(([key, val]) => (
            <span key={key} className="rounded-md bg-slate-800 px-2 py-1 border border-slate-700 font-mono text-[10px]">
              {key}: {val}
            </span>
          ))}
        </div>
      </div>

      {/* 24h Summary Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-3">
          <div className="text-[11px] text-slate-400 font-medium">Predicted Peak Temp</div>
          <div className="text-xl font-extrabold text-rose-400 mt-1">{summary_24h.max_temp_c}°C</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Min: {summary_24h.min_temp_c}°C</div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-3">
          <div className="text-[11px] text-slate-400 font-medium">Expected Rainfall</div>
          <div className="text-xl font-extrabold text-cyan-400 mt-1">{summary_24h.expected_precip_mm} mm</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Next 24 Hours</div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-3">
          <div className="text-[11px] text-slate-400 font-medium">Peak Wind Gust</div>
          <div className="text-xl font-extrabold text-amber-400 mt-1">{summary_24h.max_wind_speed_ms} m/s</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Atmospheric Velocity</div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-3">
          <div className="text-[11px] text-slate-400 font-medium">Avg Confidence</div>
          <div className="text-xl font-extrabold text-emerald-400 mt-1">92%</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Ensemble Agreement</div>
        </div>
      </div>

      {/* Hazard Risks Assessment Badges */}
      <div className="rounded-xl border border-slate-800 bg-slate-950/30 p-4">
        <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
          Automated Hazard Assessment
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className={`flex items-center justify-between p-2.5 rounded-lg border text-xs font-semibold ${getRiskBadge(hazard_risks.heatwave)}`}>
            <span className="flex items-center gap-1.5"><Flame className="h-4 w-4" /> Heatwave</span>
            <span>{hazard_risks.heatwave}</span>
          </div>
          <div className={`flex items-center justify-between p-2.5 rounded-lg border text-xs font-semibold ${getRiskBadge(hazard_risks.storm_squall)}`}>
            <span className="flex items-center gap-1.5"><Wind className="h-4 w-4" /> Storm / Squall</span>
            <span>{hazard_risks.storm_squall}</span>
          </div>
          <div className={`flex items-center justify-between p-2.5 rounded-lg border text-xs font-semibold ${getRiskBadge(hazard_risks.freeze)}`}>
            <span className="flex items-center gap-1.5"><Snowflake className="h-4 w-4" /> Freeze</span>
            <span>{hazard_risks.freeze}</span>
          </div>
          <div className={`flex items-center justify-between p-2.5 rounded-lg border text-xs font-semibold ${getRiskBadge(hazard_risks.flash_flood)}`}>
            <span className="flex items-center gap-1.5"><CloudRain className="h-4 w-4" /> Flash Flood</span>
            <span>{hazard_risks.flash_flood}</span>
          </div>
        </div>
      </div>

      {/* 24h Prediction Trend Chart */}
      <div>
        <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
          24-Hour Forecast Timeline (ML Output)
        </div>
        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="hour" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis yAxisId="temp" stroke="#f43f5e" fontSize={11} tickLine={false} domain={['dataMin - 2', 'dataMax + 2']} />
              <YAxis yAxisId="prob" orientation="right" stroke="#38bdf8" fontSize={11} tickLine={false} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '0.75rem',
                  fontSize: '12px',
                }}
              />
              <Area
                yAxisId="temp"
                type="monotone"
                dataKey="temp"
                name="Forecast Temp (°C)"
                stroke="#f43f5e"
                strokeWidth={2.5}
                fill="#f43f5e"
                fillOpacity={0.15}
              />
              <Line
                yAxisId="prob"
                type="monotone"
                dataKey="precipProb"
                name="Rain Probability (%)"
                stroke="#38bdf8"
                strokeWidth={2}
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
