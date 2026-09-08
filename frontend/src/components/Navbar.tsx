import React, { useState } from 'react';
import { CloudLightning, RefreshCw, Activity, CheckCircle, AlertCircle } from 'lucide-react';
import { alertsApi } from '../api/alerts';

interface NavbarProps {
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onRefresh, isRefreshing }) => {
  const [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'success' | 'error'>('idle');

  const handleManualIngest = async () => {
    try {
      setSyncStatus('syncing');
      await alertsApi.triggerIngestion('open_meteo');
      setSyncStatus('success');
      onRefresh();
      setTimeout(() => setSyncStatus('idle'), 4000);
    } catch (e) {
      console.error(e);
      setSyncStatus('error');
      setTimeout(() => setSyncStatus('idle'), 4000);
    }
  };

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-slate-800 bg-slate-900/80 px-6 py-3.5 backdrop-blur-md">
      <div className="flex items-center space-x-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20">
          <CloudLightning className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            WeatherPlatform
            <span className="rounded-full bg-cyan-500/10 px-2 py-0.5 text-xs font-semibold text-cyan-400 border border-cyan-500/20">
              DRF + PostGIS
            </span>
          </h1>
          <p className="text-xs text-slate-400">Meteorological Analytics & Incident Command</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="hidden md:flex items-center space-x-2 text-xs font-medium text-slate-300 bg-slate-800/80 border border-slate-700/60 px-3 py-1.5 rounded-lg">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span>Celery & Redis Active</span>
        </div>

        <button
          onClick={handleManualIngest}
          disabled={syncStatus === 'syncing' || isRefreshing}
          className="flex items-center space-x-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 px-4 py-2 text-xs font-medium text-white shadow-md shadow-blue-600/20 hover:from-cyan-500 hover:to-blue-500 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${syncStatus === 'syncing' || isRefreshing ? 'animate-spin' : ''}`} />
          <span>
            {syncStatus === 'syncing' ? 'Ingesting Open-Meteo...' : syncStatus === 'success' ? 'Ingestion Done!' : 'Sync Weather Now'}
          </span>
        </button>

        {syncStatus === 'success' && (
          <div className="flex items-center space-x-1 text-xs text-emerald-400">
            <CheckCircle className="h-4 w-4" />
          </div>
        )}
        {syncStatus === 'error' && (
          <div className="flex items-center space-x-1 text-xs text-rose-400">
            <AlertCircle className="h-4 w-4" />
          </div>
        )}
      </div>
    </header>
  );
};
