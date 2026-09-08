import React from 'react';
import {
  LayoutDashboard,
  MapPin,
  Compass,
  AlertTriangle,
  Cpu,
  BellRing,
  ShieldCheck
} from 'lucide-react';

export type TabType = 'dashboard' | 'map' | 'stations' | 'incidents' | 'predictions' | 'alerts';

interface SidebarProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  activeIncidentsCount?: number;
  activeAlertsCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  activeIncidentsCount = 0,
  activeAlertsCount = 0,
}) => {
  const navItems = [
    { id: 'dashboard' as TabType, label: 'Analytics Dashboard', icon: LayoutDashboard },
    { id: 'map' as TabType, label: 'Geospatial Radar Map', icon: MapPin },
    { id: 'stations' as TabType, label: 'Stations & Readings', icon: Compass },
    {
      id: 'incidents' as TabType,
      label: 'Incident Command',
      icon: AlertTriangle,
      badge: activeIncidentsCount > 0 ? activeIncidentsCount : undefined,
      badgeColor: 'bg-rose-500/20 text-rose-400 border border-rose-500/30',
    },
    { id: 'predictions' as TabType, label: 'ML Hazard Predictions', icon: Cpu },
    {
      id: 'alerts' as TabType,
      label: 'Alert Rules & Jobs',
      icon: BellRing,
      badge: activeAlertsCount > 0 ? activeAlertsCount : undefined,
      badgeColor: 'bg-amber-500/20 text-amber-400 border border-amber-500/30',
    },
  ];

  return (
    <aside className="w-64 flex-shrink-0 border-r border-slate-800 bg-slate-900/50 p-4 flex flex-col justify-between">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
          Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex w-full items-center justify-between rounded-xl px-3.5 py-2.5 text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`h-4 w-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && (
                <span className={`rounded-md px-1.5 py-0.5 text-[10px] font-bold ${item.badgeColor}`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-xs">
        <div className="flex items-center space-x-2 text-cyan-400 font-semibold mb-1">
          <ShieldCheck className="h-4 w-4" />
          <span>System Architecture</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          PostgreSQL 16 + PostGIS spatial layers, DRF REST layer, Celery worker beat, Scikit-Learn predictions.
        </p>
      </div>
    </aside>
  );
};
