import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import { WeatherStation, Incident } from '../types';
import { Thermometer, Wind, Droplets, Gauge, AlertTriangle, ExternalLink, Image as ImageIcon } from 'lucide-react';

// Fix Leaflet marker icons in React
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface WeatherMapProps {
  stations: WeatherStation[];
  incidents: Incident[];
  onSelectStation?: (station: WeatherStation) => void;
}

export const WeatherMap: React.FC<WeatherMapProps> = ({
  stations,
  incidents,
  onSelectStation,
}) => {
  const [showStations, setShowStations] = useState(true);
  const [showIncidents, setShowIncidents] = useState(true);
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  const getTempColor = (temp: number | null | undefined) => {
    if (temp === null || temp === undefined) return '#94a3b8';
    if (temp >= 32) return '#ef4444'; // Red
    if (temp >= 24) return '#f97316'; // Orange
    if (temp >= 16) return '#eab308'; // Amber
    if (temp >= 8) return '#10b981'; // Emerald
    if (temp >= 0) return '#06b6d4'; // Cyan
    return '#3b82f6'; // Blue
  };

  const getIncidentColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return '#ef4444';
      case 'high':
        return '#f97316';
      case 'medium':
        return '#f59e0b';
      default:
        return '#3b82f6';
    }
  };

  const filteredIncidents = incidents.filter((inc) => {
    if (!showIncidents) return false;
    if (severityFilter === 'all') return true;
    return inc.severity === severityFilter;
  });

  return (
    <div className="relative h-full w-full flex flex-col rounded-2xl overflow-hidden border border-slate-800 bg-slate-900 shadow-2xl">
      {/* Map Filter Controls Bar */}
      <div className="absolute top-4 right-4 z-[1000] flex flex-wrap items-center gap-2 rounded-xl bg-slate-900/90 p-2.5 backdrop-blur-md border border-slate-800 shadow-xl text-xs">
        <label className="flex items-center space-x-2 cursor-pointer text-slate-300 font-medium px-2 py-1 hover:bg-slate-800 rounded-lg">
          <input
            type="checkbox"
            checked={showStations}
            onChange={(e) => setShowStations(e.target.checked)}
            className="rounded border-slate-700 text-cyan-500 focus:ring-0"
          />
          <span>Stations ({stations.length})</span>
        </label>

        <label className="flex items-center space-x-2 cursor-pointer text-slate-300 font-medium px-2 py-1 hover:bg-slate-800 rounded-lg">
          <input
            type="checkbox"
            checked={showIncidents}
            onChange={(e) => setShowIncidents(e.target.checked)}
            className="rounded border-slate-700 text-rose-500 focus:ring-0"
          />
          <span>Incidents ({incidents.length})</span>
        </label>

        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="rounded-lg bg-slate-800 border border-slate-700 px-2.5 py-1 text-slate-200 focus:outline-none"
        >
          <option value="all">All Severities</option>
          <option value="critical">Critical Only</option>
          <option value="high">High & Above</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Leaflet Map */}
      <div className="flex-1 w-full h-[600px] min-h-[500px]">
        <MapContainer
          center={[25.0, 10.0]}
          zoom={2.5}
          scrollWheelZoom={true}
          className="w-full h-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          {/* Weather Station Markers */}
          {showStations &&
            stations.map((station) => {
              if (station.latitude === null || station.longitude === null) return null;
              const temp = station.latest_reading?.temperature_c;
              const color = getTempColor(temp);

              return (
                <CircleMarker
                  key={`station-${station.id}`}
                  center={[station.latitude, station.longitude]}
                  radius={9}
                  pathOptions={{
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.85,
                    weight: 2,
                  }}
                >
                  <Popup>
                    <div className="p-1 space-y-2 min-w-[200px] text-slate-100">
                      <div className="flex items-center justify-between border-b border-slate-700 pb-1.5">
                        <span className="font-bold text-sm text-cyan-400">{station.code}</span>
                        <span className="text-[10px] uppercase font-semibold text-slate-400">
                          {station.is_active ? 'Active' : 'Offline'}
                        </span>
                      </div>
                      <p className="font-medium text-xs text-slate-200">{station.name}</p>

                      {station.latest_reading ? (
                        <div className="grid grid-cols-2 gap-2 text-xs py-1">
                          <div className="flex items-center space-x-1.5 text-rose-400">
                            <Thermometer className="h-3.5 w-3.5" />
                            <span className="font-bold">
                              {station.latest_reading.temperature_c !== null
                                ? `${station.latest_reading.temperature_c}°C`
                                : '--'}
                            </span>
                          </div>
                          <div className="flex items-center space-x-1.5 text-cyan-400">
                            <Droplets className="h-3.5 w-3.5" />
                            <span>
                              {station.latest_reading.humidity_pct !== null
                                ? `${station.latest_reading.humidity_pct}%`
                                : '--'}
                            </span>
                          </div>
                          <div className="flex items-center space-x-1.5 text-amber-400">
                            <Wind className="h-3.5 w-3.5" />
                            <span>
                              {station.latest_reading.wind_speed_ms !== null
                                ? `${station.latest_reading.wind_speed_ms} m/s`
                                : '--'}
                            </span>
                          </div>
                          <div className="flex items-center space-x-1.5 text-purple-400">
                            <Gauge className="h-3.5 w-3.5" />
                            <span>
                              {station.latest_reading.pressure_hpa !== null
                                ? `${Math.round(station.latest_reading.pressure_hpa)} hPa`
                                : '--'}
                            </span>
                          </div>
                        </div>
                      ) : (
                        <p className="text-xs text-slate-400 italic">No observation data ingested</p>
                      )}

                      {onSelectStation && (
                        <button
                          onClick={() => onSelectStation(station)}
                          className="mt-2 flex w-full items-center justify-center space-x-1 rounded-lg bg-cyan-600/80 px-2.5 py-1.5 text-[11px] font-semibold text-white hover:bg-cyan-500"
                        >
                          <span>View Charts & ML Forecast</span>
                          <ExternalLink className="h-3 w-3" />
                        </button>
                      )}
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}

          {/* Incident Hazard Polygons */}
          {filteredIncidents.map((incident) => {
            const color = getIncidentColor(incident.severity);

            // If affected_area polygon exists in GeoJSON format
            if (incident.affected_area && incident.affected_area.coordinates) {
              const coords = incident.affected_area.coordinates[0].map(
                (coord: [number, number]) => [coord[1], coord[0]] as [number, number]
              );

              return (
                <Polygon
                  key={`incident-poly-${incident.id}`}
                  positions={coords}
                  pathOptions={{
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.28,
                    weight: 2,
                    dashArray: '4, 6',
                  }}
                >
                  <Popup>
                    <div className="p-1.5 space-y-2 min-w-[220px]">
                      <div className="flex items-center justify-between">
                        <span
                          className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider text-white"
                          style={{ backgroundColor: color }}
                        >
                          {incident.severity}
                        </span>
                        <span className="text-[10px] text-slate-400 uppercase font-semibold">
                          {incident.status}
                        </span>
                      </div>
                      <h4 className="font-bold text-xs text-white flex items-center gap-1.5">
                        <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
                        {incident.title}
                      </h4>
                      <p className="text-[11px] text-slate-300 line-clamp-3">{incident.description}</p>
                      {incident.image && (
                        <div className="mt-1 overflow-hidden rounded-md border border-slate-700">
                          <img
                            src={incident.image}
                            alt={incident.title}
                            className="h-28 w-full object-cover"
                          />
                        </div>
                      )}
                    </div>
                  </Popup>
                </Polygon>
              );
            }

            // Fallback to centroid marker if affected_area coordinates are not an explicit polygon array
            if (incident.centroid) {
              return (
                <Marker
                  key={`incident-point-${incident.id}`}
                  position={[incident.centroid.latitude, incident.centroid.longitude]}
                >
                  <Popup>
                    <div className="p-1 space-y-1">
                      <span className="font-bold text-xs text-rose-400">[{incident.severity}]</span>
                      <p className="text-xs font-semibold text-white">{incident.title}</p>
                      <p className="text-[11px] text-slate-300">{incident.description}</p>
                    </div>
                  </Popup>
                </Marker>
              );
            }

            return null;
          })}
        </MapContainer>
      </div>
    </div>
  );
};
