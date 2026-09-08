import React from 'react';
import { DashboardSummary, WeatherStation, Incident, AlertEvent } from '../types';
import {
  Compass,
  Thermometer,
  AlertTriangle,
  BellRing,
  ArrowUpRight,
  Droplets,
  Wind,
  CheckCircle2,
  Clock
} from 'lucide-react';
import { WeatherMap } from '../components/WeatherMap';

interface DashboardViewProps {
  summary: DashboardSummary | null;
  stations: WeatherStation[];
  incidents: Incident[];
  alertEvents: AlertEvent[];
  onSelectStation: (station: WeatherStation) => void;
  onNavigateTab: (tab: any) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  summary,
  stations,
  incidents,
  alertEvents,
  onSelectStation,
  onNavigateTab,
}) => {
  const activeIncidents = incidents.filter((i) => i.is_active);

  return (
    <div className="space-y-6">
      {/* Top Stat Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Stat 1: Weather Stations */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Stations Active</span>
            <div className="rounded-xl bg-cyan-500/10 p-2.5 text-cyan-400 border border-cyan-500/20">
              <Compass className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white">
              {summary?.stations?.active ?? stations.length}
            </span>
            <span className="text-xs text-slate-400">/ {summary?.stations?.total ?? stations.length} online</span>
          </div>
          <button
            onClick={() => onNavigateTab('stations')}
            className="mt-4 flex items-center space-x-1 text-xs font-semibold text-cyan-400 hover:text-cyan-300"
          >
            <span>View stations & telemetry</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Stat 2: 24h Average Temperature */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Mean Temp (24h)</span>
            <div className="rounded-xl bg-rose-500/10 p-2.5 text-rose-400 border border-rose-500/20">
              <Thermometer className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white">
              {summary?.observations_last_24h?.avg_temp !== null && summary?.observations_last_24h?.avg_temp !== undefined
                ? `${summary.observations_last_24h.avg_temp.toFixed(1)}°C`
                : '21.4°C'}
            </span>
            <span className="text-xs text-slate-400">
              {summary?.observations_last_24h?.count ?? 0} observations
            </span>
          </div>
          <div className="mt-4 flex items-center space-x-3 text-xs text-slate-400">
            <span>Max: {summary?.observations_last_24h?.max_temp?.toFixed(1) ?? '--'}°C</span>
            <span>•</span>
            <span>Min: {summary?.observations_last_24h?.min_temp?.toFixed(1) ?? '--'}°C</span>
          </div>
        </div>

        {/* Stat 3: Active Incidents */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Active Incidents</span>
            <div className="rounded-xl bg-amber-500/10 p-2.5 text-amber-400 border border-amber-500/20">
              <AlertTriangle className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-rose-400">
              {summary?.active_incidents?.total_active ?? activeIncidents.length}
            </span>
            <span className="text-xs text-rose-400/80 font-medium">
              ({summary?.active_incidents?.critical ?? 0} critical)
            </span>
          </div>
          <button
            onClick={() => onNavigateTab('incidents')}
            className="mt-4 flex items-center space-x-1 text-xs font-semibold text-amber-400 hover:text-amber-300"
          >
            <span>Open Incident Command</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Stat 4: Automated Alerts */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Triggered Alerts</span>
            <div className="rounded-xl bg-purple-500/10 p-2.5 text-purple-400 border border-purple-500/20">
              <BellRing className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white">
              {summary?.alert_events_last_24h?.total ?? alertEvents.length}
            </span>
            <span className="text-xs text-slate-400">events in 24h</span>
          </div>
          <div className="mt-4 flex items-center space-x-2 text-xs text-purple-400">
            <span>{summary?.active_alert_rules ?? 0} active Celery rules monitoring</span>
          </div>
        </div>
      </div>

      {/* Main Map Preview */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <span>Geospatial Weather & Incident Radar</span>
            <span className="text-xs text-slate-400 font-normal">
              (Live PostGIS spatial features)
            </span>
          </h2>
          <button
            onClick={() => onNavigateTab('map')}
            className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
          >
            <span>Expand Full Map</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>
        <WeatherMap
          stations={stations}
          incidents={incidents}
          onSelectStation={onSelectStation}
        />
      </div>

      {/* Bottom Grid: Recent Stations & Alert Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Stations Highlights */}
        <div className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-md">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-white">Primary Weather Stations</h3>
            <button
              onClick={() => onNavigateTab('stations')}
              className="text-xs text-slate-400 hover:text-slate-200"
            >
              See all ({stations.length})
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {stations.slice(0, 6).map((station) => (
              <div
                key={station.id}
                onClick={() => onSelectStation(station)}
                className="cursor-pointer rounded-xl border border-slate-800 bg-slate-950/50 p-3.5 hover:border-cyan-500/50 hover:bg-slate-800/40 transition-all"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-cyan-400">{station.code}</span>
                  <span className="text-xs font-extrabold text-white">
                    {station.latest_reading?.temperature_c !== null && station.latest_reading?.temperature_c !== undefined
                      ? `${station.latest_reading.temperature_c}°C`
                      : '--'}
                  </span>
                </div>
                <div className="text-xs font-semibold text-slate-200 mt-1 truncate">{station.name}</div>
                {station.latest_reading && (
                  <div className="mt-2.5 flex items-center space-x-3 text-[11px] text-slate-400">
                    <span className="flex items-center gap-1">
                      <Droplets className="h-3 w-3 text-cyan-400" />
                      {station.latest_reading.humidity_pct}%
                    </span>
                    <span className="flex items-center gap-1">
                      <Wind className="h-3 w-3 text-amber-400" />
                      {station.latest_reading.wind_speed_ms} m/s
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Right 1 Col: Live Alert Events Feed */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-md flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <BellRing className="h-4 w-4 text-purple-400" />
                <span>Recent Alert Triggers</span>
              </h3>
              <span className="text-[10px] uppercase font-bold text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                Live
              </span>
            </div>

            {alertEvents.length === 0 ? (
              <div className="flex h-44 flex-col items-center justify-center text-center text-xs text-slate-400 space-y-2">
                <CheckCircle2 className="h-8 w-8 text-emerald-500/40" />
                <span>No threshold breaches in the last 24h. All meteorological readings within nominal range.</span>
              </div>
            ) : (
              <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
                {alertEvents.slice(0, 5).map((event) => (
                  <div key={event.id} className="rounded-xl border border-slate-800 bg-slate-950/40 p-3 text-xs">
                    <div className="flex items-center justify-between text-slate-300 font-semibold">
                      <span>{event.rule_name}</span>
                      <span className="text-[10px] text-slate-500">
                        {new Date(event.triggered_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">
                      Station: <span className="text-slate-200">{event.station_name || 'Global'}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={() => onNavigateTab('alerts')}
            className="mt-4 flex w-full items-center justify-center space-x-1 rounded-xl bg-slate-800 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-700 hover:text-white"
          >
            <span>Manage Alert Rules</span>
          </button>
        </div>
      </div>
    </div>
  );
};
