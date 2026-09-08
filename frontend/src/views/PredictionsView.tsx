import React, { useState, useEffect } from 'react';
import { WeatherStation, PredictionResult } from '../types';
import { weatherApi } from '../api/weather';
import { PredictionCard } from '../components/PredictionCard';
import { BrainCircuit, Cpu, RefreshCw, Sparkles, AlertTriangle, Layers } from 'lucide-react';

interface PredictionsViewProps {
  stations: WeatherStation[];
  selectedStation: WeatherStation | null;
  onSelectStation: (station: WeatherStation) => void;
}

export const PredictionsView: React.FC<PredictionsViewProps> = ({
  stations,
  selectedStation,
  onSelectStation,
}) => {
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);

  const activeStation = selectedStation || stations[0];

  useEffect(() => {
    if (activeStation) {
      loadPrediction(activeStation.id);
    }
  }, [activeStation?.id]);

  const loadPrediction = async (stationId: number) => {
    try {
      setLoading(true);
      const res = await weatherApi.getStationPrediction(stationId);
      setPrediction(res);
      setLoading(false);
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
            <BrainCircuit className="h-6 w-6 text-purple-400" />
            <span>Machine Learning Meteorological Forecasting</span>
          </h2>
          <p className="text-xs text-slate-400">
            Ensemble regressions trained on telemetry lag-variables and solar diurnal harmonic dynamics
          </p>
        </div>

        {activeStation && (
          <button
            onClick={() => loadPrediction(activeStation.id)}
            disabled={loading}
            className="flex items-center space-x-2 rounded-xl bg-purple-600 px-4 py-2 text-xs font-bold text-white shadow-lg shadow-purple-600/20 hover:bg-purple-500 disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Executing ML Inference...' : 'Re-run Inference'}</span>
          </button>
        )}
      </div>

      {/* Station Selector Bar */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2">
        {stations.map((s) => {
          const isSelected = activeStation?.id === s.id;
          return (
            <button
              key={s.id}
              onClick={() => onSelectStation(s)}
              className={`flex-shrink-0 rounded-xl px-3.5 py-2 text-xs font-semibold transition-all ${
                isSelected
                  ? 'bg-purple-600/20 text-purple-300 border border-purple-500/50 shadow-md shadow-purple-600/10'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              <span className="font-mono font-bold mr-1.5">{s.code}</span>
              <span>{s.name}</span>
            </button>
          );
        })}
      </div>

      {/* Main Prediction Display */}
      {loading ? (
        <div className="flex h-72 flex-col items-center justify-center rounded-2xl border border-slate-800 bg-slate-900/40 text-slate-400 space-y-3">
          <Cpu className="h-8 w-8 text-purple-400 animate-pulse" />
          <span className="text-xs font-medium">Extracting lag feature matrix & executing model inference...</span>
        </div>
      ) : prediction ? (
        <PredictionCard prediction={prediction} />
      ) : (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-8 text-center text-xs text-slate-400">
          Select a station above to compute 24-hour ML predictions.
        </div>
      )}

      {/* ML Pipeline Explainer Card */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5 text-xs text-slate-300 space-y-3">
        <h4 className="font-bold text-white flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-purple-400" />
          <span>About the Scikit-Learn Prediction Architecture</span>
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-[11px] text-slate-400">
          <div className="rounded-xl bg-slate-950/60 p-3 border border-slate-800/80">
            <span className="font-bold text-slate-200 block mb-1">Lag Feature Matrix</span>
            Models extract \(t-1\), \(t-2\), \(t-3\) hour temperatures, barometric pressure slopes, and relative humidity indices from historical observations.
          </div>
          <div className="rounded-xl bg-slate-950/60 p-3 border border-slate-800/80">
            <span className="font-bold text-slate-200 block mb-1">Diurnal Atmospheric Harmonics</span>
            Applies sinusoidal astronomical solar irradiance cycles (\(\sin(2\pi h / 24)\)) to capture peak radiative heating and nighttime cooling.
          </div>
          <div className="rounded-xl bg-slate-950/60 p-3 border border-slate-800/80">
            <span className="font-bold text-slate-200 block mb-1">Hazard Risk Classification</span>
            Evaluates compound thresholds (e.g. pressure drops + high wind velocities) for automatic heatwave, squall, and flash flood alerts.
          </div>
        </div>
      </div>
    </div>
  );
};
