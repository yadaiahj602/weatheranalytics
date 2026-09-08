import React, { useState } from 'react';
import { X, Upload, AlertTriangle, Image as ImageIcon } from 'lucide-react';
import { incidentsApi } from '../api/incidents';

interface IncidentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const IncidentModal: React.FC<IncidentModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [incidentType, setIncidentType] = useState('storm');
  const [severity, setSeverity] = useState('high');
  const [status, setStatus] = useState('open');
  const [latitude, setLatitude] = useState('40.7128');
  const [longitude, setLongitude] = useState('-74.0060');
  const [radiusKm, setRadiusKm] = useState('15');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setIsSubmitting(true);

    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('description', description);
      formData.append('incident_type', incidentType);
      formData.append('severity', severity);
      formData.append('status', status);
      formData.append('start_time', new Date().toISOString());

      // Generate a polygon around the center point for PostGIS
      const lat = parseFloat(latitude);
      const lon = parseFloat(longitude);
      const offset = (parseFloat(radiusKm) / 111.0); // approx degrees

      const polygonGeoJSON = {
        type: 'Polygon',
        coordinates: [
          [
            [lon - offset, lat - offset],
            [lon + offset, lat - offset],
            [lon + offset, lat + offset],
            [lon - offset, lat + offset],
            [lon - offset, lat - offset],
          ],
        ],
      };
      formData.append('affected_area', JSON.stringify(polygonGeoJSON));

      if (imageFile) {
        formData.append('image', imageFile);
      }

      await incidentsApi.createIncident(formData);
      setIsSubmitting(false);
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || 'Failed to submit incident report');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
      <div className="relative w-full max-w-xl rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-2 text-rose-400">
            <AlertTriangle className="h-5 w-5" />
            <h3 className="text-lg font-bold text-white">Create Incident Report</h3>
          </div>
          <button onClick={onClose} className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white">
            <X className="h-5 w-5" />
          </button>
        </div>

        {errorMsg && (
          <div className="mt-4 rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Incident Title</label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Flash Flood Along River Corridor"
              className="w-full rounded-xl border border-slate-700 bg-slate-800/80 px-3 py-2 text-xs text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Type</label>
              <select
                value={incidentType}
                onChange={(e) => setIncidentType(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-800/80 px-3 py-2 text-xs text-white focus:outline-none"
              >
                <option value="flood">Flood</option>
                <option value="storm">Storm</option>
                <option value="heatwave">Heatwave</option>
                <option value="drought">Drought</option>
                <option value="tornado">Tornado</option>
                <option value="blizzard">Blizzard</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Severity</label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-800/80 px-3 py-2 text-xs text-white focus:outline-none"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Description</label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Detailed description of weather damage, affected assets, or evacuation advisories..."
              className="w-full rounded-xl border border-slate-700 bg-slate-800/80 px-3 py-2 text-xs text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
            />
          </div>

          {/* Coordinates & Area */}
          <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-3 space-y-2">
            <span className="text-[11px] font-semibold uppercase text-slate-400">PostGIS Geographic Polygon</span>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="block text-[10px] text-slate-400">Latitude</label>
                <input
                  type="text"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-[10px] text-slate-400">Longitude</label>
                <input
                  type="text"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-[10px] text-slate-400">Radius (km)</label>
                <input
                  type="text"
                  value={radiusKm}
                  onChange={(e) => setRadiusKm(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-xs text-white"
                />
              </div>
            </div>
          </div>

          {/* Image / File Upload (Step 6) */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Incident Photo / Damage Evidence
            </label>
            <div className="flex items-center space-x-3">
              <label className="flex cursor-pointer items-center space-x-2 rounded-xl border border-dashed border-slate-700 bg-slate-800/50 px-4 py-2.5 text-xs text-slate-300 hover:border-cyan-500 hover:bg-slate-800">
                <Upload className="h-4 w-4 text-cyan-400" />
                <span>{imageFile ? imageFile.name : 'Choose Image File'}</span>
                <input type="file" accept="image/*" onChange={handleImageChange} className="hidden" />
              </label>
              {imagePreview && (
                <div className="relative h-10 w-10 overflow-hidden rounded-lg border border-slate-700">
                  <img src={imagePreview} alt="Preview" className="h-full w-full object-cover" />
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-end space-x-3 border-t border-slate-800 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl px-4 py-2 text-xs font-semibold text-slate-400 hover:bg-slate-800 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="rounded-xl bg-gradient-to-r from-rose-600 to-amber-600 px-5 py-2 text-xs font-bold text-white shadow-lg shadow-rose-600/20 hover:from-rose-500 hover:to-amber-500 disabled:opacity-50"
            >
              {isSubmitting ? 'Submitting...' : 'Register Incident'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
