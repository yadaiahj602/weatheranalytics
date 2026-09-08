import React, { useState } from 'react';
import { Incident } from '../types';
import { incidentsApi } from '../api/incidents';
import { IncidentModal } from '../components/IncidentModal';
import {
  AlertTriangle,
  Plus,
  Filter,
  CheckCircle,
  Clock,
  MapPin,
  Image as ImageIcon,
  Flame,
  Wind,
  CloudRain
} from 'lucide-react';

interface IncidentsViewProps {
  incidents: Incident[];
  onRefresh: () => void;
}

export const IncidentsView: React.FC<IncidentsViewProps> = ({ incidents, onRefresh }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [expandedImage, setExpandedImage] = useState<string | null>(null);

  const filteredIncidents = incidents.filter((inc) => {
    if (selectedSeverity !== 'all' && inc.severity !== selectedSeverity) return false;
    if (selectedStatus !== 'all' && inc.status !== selectedStatus) return false;
    return true;
  });

  const handleUpdateStatus = async (id: number, newStatus: string) => {
    try {
      await incidentsApi.updateIncidentStatus(id, newStatus);
      onRefresh();
    } catch (e) {
      console.error(e);
    }
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev.toLowerCase()) {
      case 'critical':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/40';
      case 'high':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/40';
      case 'medium':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      default:
        return 'bg-blue-500/20 text-blue-400 border-blue-500/40';
    }
  };

  return (
    <div className="space-y-6">
      {/* View Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
            <AlertTriangle className="h-6 w-6 text-rose-400" />
            <span>Incident Command & Hazard Reports</span>
          </h2>
          <p className="text-xs text-slate-400">
            Real-time hazard zones, damage logs, and field attachments
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center space-x-2 rounded-xl bg-gradient-to-r from-rose-600 to-amber-600 px-4 py-2.5 text-xs font-bold text-white shadow-lg shadow-rose-600/20 hover:from-rose-500 hover:to-amber-500 transition-all"
        >
          <Plus className="h-4 w-4" />
          <span>Report New Incident</span>
        </button>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-slate-800 bg-slate-900/60 p-3.5 backdrop-blur-md text-xs">
        <div className="flex items-center space-x-1.5 text-slate-400 font-medium">
          <Filter className="h-3.5 w-3.5" />
          <span>Filter:</span>
        </div>

        <select
          value={selectedSeverity}
          onChange={(e) => setSelectedSeverity(e.target.value)}
          className="rounded-lg bg-slate-800 border border-slate-700 px-3 py-1.5 text-white focus:outline-none"
        >
          <option value="all">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="rounded-lg bg-slate-800 border border-slate-700 px-3 py-1.5 text-white focus:outline-none"
        >
          <option value="all">All Statuses</option>
          <option value="open">Open</option>
          <option value="monitoring">Monitoring</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>

        <span className="text-slate-500 ml-auto font-mono text-[11px]">
          Showing {filteredIncidents.length} of {incidents.length} incidents
        </span>
      </div>

      {/* Incidents Grid */}
      {filteredIncidents.length === 0 ? (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-12 text-center text-xs text-slate-400">
          No incidents match the active filters.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredIncidents.map((incident) => (
            <div
              key={incident.id}
              className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 shadow-xl backdrop-blur-md flex flex-col justify-between hover:border-slate-700 transition-all"
            >
              <div className="space-y-3">
                {/* Top Badges */}
                <div className="flex items-center justify-between">
                  <span
                    className={`rounded-lg px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider border ${getSeverityBadge(
                      incident.severity
                    )}`}
                  >
                    {incident.severity}
                  </span>
                  <span className="rounded-md bg-slate-800 px-2 py-0.5 text-[10px] font-semibold text-slate-300 uppercase">
                    {incident.status}
                  </span>
                </div>

                {/* Title & Description */}
                <div>
                  <h3 className="font-bold text-sm text-white leading-snug">{incident.title}</h3>
                  <div className="mt-1 flex items-center space-x-2 text-[11px] text-cyan-400 uppercase font-semibold">
                    <span>Type: {incident.incident_type}</span>
                  </div>
                  <p className="mt-2 text-xs text-slate-300 line-clamp-3 leading-relaxed">
                    {incident.description || 'No description provided.'}
                  </p>
                </div>

                {/* Image Attachment (Step 6) */}
                {incident.image && (
                  <div
                    onClick={() => setExpandedImage(incident.image!)}
                    className="relative cursor-pointer overflow-hidden rounded-xl border border-slate-700 group h-36"
                  >
                    <img
                      src={incident.image}
                      alt={incident.title}
                      className="h-full w-full object-cover group-hover:scale-105 transition-all duration-300"
                    />
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-semibold">
                      Click to View Full Photo
                    </div>
                  </div>
                )}
              </div>

              {/* Footer & Status Actions */}
              <div className="mt-4 border-t border-slate-800 pt-3 space-y-2">
                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {new Date(incident.start_time).toLocaleDateString()}
                  </span>
                  {incident.centroid && (
                    <span className="flex items-center gap-1 text-slate-400">
                      <MapPin className="h-3 w-3" />
                      PostGIS Polygon
                    </span>
                  )}
                </div>

                <div className="flex items-center space-x-2 pt-1">
                  {incident.status !== 'resolved' && (
                    <button
                      onClick={() => handleUpdateStatus(incident.id, 'resolved')}
                      className="flex-1 rounded-lg bg-emerald-600/20 py-1.5 text-center text-[11px] font-bold text-emerald-300 border border-emerald-500/30 hover:bg-emerald-600/30"
                    >
                      Mark Resolved
                    </button>
                  )}
                  {incident.status !== 'monitoring' && incident.status !== 'resolved' && (
                    <button
                      onClick={() => handleUpdateStatus(incident.id, 'monitoring')}
                      className="flex-1 rounded-lg bg-amber-600/20 py-1.5 text-center text-[11px] font-bold text-amber-300 border border-amber-500/30 hover:bg-amber-600/30"
                    >
                      Monitoring
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Incident Creation Modal */}
      <IncidentModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={onRefresh}
      />

      {/* Lightbox Modal for Photo */}
      {expandedImage && (
        <div
          onClick={() => setExpandedImage(null)}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4 cursor-pointer backdrop-blur-md"
        >
          <img src={expandedImage} alt="Enlarged evidence" className="max-h-[85vh] max-w-[85vw] rounded-2xl shadow-2xl border border-slate-700" />
        </div>
      )}
    </div>
  );
};
