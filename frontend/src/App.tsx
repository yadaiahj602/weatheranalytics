import React, { useState, useEffect } from 'react';
import { WeatherStation, Incident, AlertRule, AlertEvent, DashboardSummary } from './types';
import { weatherApi } from './api/weather';
import { incidentsApi } from './api/incidents';
import { alertsApi } from './api/alerts';
import { dashboardApi } from './api/dashboard';
import { Navbar } from './components/Navbar';
import { Sidebar, TabType } from './components/Sidebar';
import { WeatherMap } from './components/WeatherMap';
import { DashboardView } from './views/DashboardView';
import { StationsView } from './views/StationsView';
import { IncidentsView } from './views/IncidentsView';
import { PredictionsView } from './views/PredictionsView';
import { AlertsView } from './views/AlertsView';
import { RefreshCw, ServerCrash } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [stations, setStations] = useState<WeatherStation[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [alertRules, setAlertRules] = useState<AlertRule[]>([]);
  const [alertEvents, setAlertEvents] = useState<AlertEvent[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [selectedStation, setSelectedStation] = useState<WeatherStation | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadAllData = async (isInitial = false) => {
    try {
      if (isInitial) setIsLoading(true);
      else setIsRefreshing(true);
      setError(null);

      // Load all data concurrently
      const [stData, incData, rulesData, eventsData, sumData] = await Promise.all([
        weatherApi.getStations().catch(() => []),
        incidentsApi.getIncidents().catch(() => []),
        alertsApi.getRules().catch(() => []),
        alertsApi.getEvents().catch(() => []),
        dashboardApi.getSummary().catch(() => null),
      ]);

      setStations(stData);
      setIncidents(incData);
      setAlertRules(rulesData);
      setAlertEvents(eventsData);
      setSummary(sumData);

      if (stData.length > 0 && !selectedStation) {
        setSelectedStation(stData[0]);
      }
    } catch (err: any) {
      console.error('Failed to load platform data:', err);
      setError('Could not connect to backend DRF API service.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadAllData(true);
  }, []);

  const handleSelectStationAndTab = (station: WeatherStation, tab: TabType = 'stations') => {
    setSelectedStation(station);
    setActiveTab(tab);
  };

  return (
    <div className="flex h-screen flex-col bg-slate-950 text-slate-100 overflow-hidden">
      {/* Top Navigation */}
      <Navbar onRefresh={() => loadAllData(false)} isRefreshing={isRefreshing} />

      {/* Main Body with Sidebar + Content */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          activeIncidentsCount={incidents.filter((i) => i.is_active).length}
          activeAlertsCount={alertEvents.length}
        />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          {isLoading ? (
            <div className="flex h-full flex-col items-center justify-center space-y-4 text-slate-400">
              <RefreshCw className="h-10 w-10 text-cyan-400 animate-spin" />
              <div className="text-center">
                <p className="font-bold text-white text-sm">Connecting to Weather Analytics Engine...</p>
                <p className="text-xs text-slate-500">Querying PostGIS spatial layers & DRF telemetry endpoints</p>
              </div>
            </div>
          ) : error && stations.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center space-y-4 text-slate-400">
              <ServerCrash className="h-12 w-12 text-rose-400" />
              <div className="text-center max-w-md">
                <p className="font-bold text-white text-base">Backend Connection Notice</p>
                <p className="text-xs text-slate-400 mt-1">{error}</p>
                <p className="text-xs text-slate-500 mt-2">
                  Make sure Django server is running (`python manage.py runserver` or docker-compose) with database migrated and seeded.
                </p>
                <button
                  onClick={() => loadAllData(true)}
                  className="mt-4 rounded-xl bg-cyan-600 px-4 py-2 text-xs font-bold text-white hover:bg-cyan-500"
                >
                  Retry Connection
                </button>
              </div>
            </div>
          ) : (
            <>
              {activeTab === 'dashboard' && (
                <DashboardView
                  summary={summary}
                  stations={stations}
                  incidents={incidents}
                  alertEvents={alertEvents}
                  onSelectStation={(s) => handleSelectStationAndTab(s, 'stations')}
                  onNavigateTab={setActiveTab}
                />
              )}

              {activeTab === 'map' && (
                <div className="h-full flex flex-col space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-extrabold text-white">Full-Screen Geospatial Radar</h2>
                      <p className="text-xs text-slate-400">
                        Interactive Leaflet map displaying active stations and PostGIS incident polygons
                      </p>
                    </div>
                  </div>
                  <div className="flex-1 min-h-[650px]">
                    <WeatherMap
                      stations={stations}
                      incidents={incidents}
                      onSelectStation={(s) => handleSelectStationAndTab(s, 'stations')}
                    />
                  </div>
                </div>
              )}

              {activeTab === 'stations' && (
                <StationsView
                  stations={stations}
                  selectedStation={selectedStation}
                  onSelectStation={setSelectedStation}
                  onNavigateToPredict={(s) => handleSelectStationAndTab(s, 'predictions')}
                />
              )}

              {activeTab === 'incidents' && (
                <IncidentsView
                  incidents={incidents}
                  onRefresh={() => loadAllData(false)}
                />
              )}

              {activeTab === 'predictions' && (
                <PredictionsView
                  stations={stations}
                  selectedStation={selectedStation}
                  onSelectStation={setSelectedStation}
                />
              )}

              {activeTab === 'alerts' && (
                <AlertsView
                  rules={alertRules}
                  events={alertEvents}
                  onRefresh={() => loadAllData(false)}
                />
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
};
