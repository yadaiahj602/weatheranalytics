import React, { useState, useEffect } from 'react';
import { AlertRule, AlertEvent, IngestionJob } from '../types';
import { alertsApi } from '../api/alerts';
import {
  BellRing,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  Send,
  Plus,
  Radio,
  Server
} from 'lucide-react';

interface AlertsViewProps {
  rules: AlertRule[];
  events: AlertEvent[];
  onRefresh: () => void;
}

export const AlertsView: React.FC<AlertsViewProps> = ({ rules, events, onRefresh }) => {
  const [jobs, setJobs] = useState<IngestionJob[]>([]);
  const [activeSubTab, setActiveSubTab] = useState<'rules' | 'events' | 'jobs'>('rules');

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const data = await alertsApi.getIngestionJobs();
      setJobs(data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div>
        <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
          <BellRing className="h-6 w-6 text-purple-400" />
          <span>Alert Automation & Celery Pipeline Jobs</span>
        </h2>
        <p className="text-xs text-slate-400">
          Threshold monitoring rules, automated multi-channel dispatch, and Celery beat periodic executions
        </p>
      </div>

      {/* Sub Tabs */}
      <div className="flex space-x-2 border-b border-slate-800 pb-3 text-xs">
        <button
          onClick={() => setActiveSubTab('rules')}
          className={`rounded-xl px-4 py-2 font-bold transition-all ${
            activeSubTab === 'rules'
              ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/20'
              : 'text-slate-400 hover:bg-slate-800'
          }`}
        >
          Configured Alert Rules ({rules.length})
        </button>
        <button
          onClick={() => setActiveSubTab('events')}
          className={`rounded-xl px-4 py-2 font-bold transition-all ${
            activeSubTab === 'events'
              ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/20'
              : 'text-slate-400 hover:bg-slate-800'
          }`}
        >
          Triggered Event History ({events.length})
        </button>
        <button
          onClick={() => setActiveSubTab('jobs')}
          className={`rounded-xl px-4 py-2 font-bold transition-all ${
            activeSubTab === 'jobs'
              ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/20'
              : 'text-slate-400 hover:bg-slate-800'
          }`}
        >
          Ingestion Job Logs ({jobs.length})
        </button>
      </div>

      {/* Tab Content */}
      {activeSubTab === 'rules' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {rules.map((rule) => (
              <div
                key={rule.id}
                className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 shadow-xl backdrop-blur-md flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[11px] font-bold text-purple-400 uppercase">
                      {rule.condition_type}
                    </span>
                    <span
                      className={`rounded-md px-2 py-0.5 text-[10px] font-bold ${
                        rule.is_active
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-slate-800 text-slate-500'
                      }`}
                    >
                      {rule.is_active ? 'Active' : 'Disabled'}
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-white mt-2">{rule.name}</h3>
                  <p className="text-xs text-slate-400 mt-1">{rule.description || 'Threshold rule'}</p>

                  <div className="mt-4 rounded-xl bg-slate-950/60 p-3 border border-slate-800/80 space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Trigger Threshold:</span>
                      <span className="font-bold text-white">{rule.threshold}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Target Station:</span>
                      <span className="text-cyan-400 font-medium">{rule.station_name || 'All Stations'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Channel:</span>
                      <span className="font-semibold text-slate-300 uppercase">{rule.channel}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeSubTab === 'events' && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="py-2.5 px-3">Rule Name</th>
                  <th className="py-2.5 px-3">Condition</th>
                  <th className="py-2.5 px-3">Station</th>
                  <th className="py-2.5 px-3">Triggered At</th>
                  <th className="py-2.5 px-3">Notification Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {events.map((ev) => (
                  <tr key={ev.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 font-semibold text-white">{ev.rule_name}</td>
                    <td className="py-2.5 px-3 font-mono text-purple-400">{ev.condition_type} &gt; {ev.threshold}</td>
                    <td className="py-2.5 px-3 text-cyan-400">{ev.station_name}</td>
                    <td className="py-2.5 px-3 font-mono text-slate-400">{new Date(ev.triggered_at).toLocaleString()}</td>
                    <td className="py-2.5 px-3">
                      <span className="rounded bg-emerald-500/10 px-2 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/20">
                        {ev.notify_status.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeSubTab === 'jobs' && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="py-2.5 px-3">Job ID</th>
                  <th className="py-2.5 px-3">Source</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Started (UTC)</th>
                  <th className="py-2.5 px-3">Records Ingested</th>
                  <th className="py-2.5 px-3">Error</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 font-mono text-slate-400">#{job.id}</td>
                    <td className="py-2.5 px-3 font-semibold text-cyan-400 uppercase">{job.source}</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`rounded px-2 py-0.5 text-[10px] font-bold uppercase ${
                          job.status === 'success'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : job.status === 'running'
                            ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 animate-pulse'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        }`}
                      >
                        {job.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-mono text-slate-400">
                      {job.started_at ? new Date(job.started_at).toLocaleString() : '--'}
                    </td>
                    <td className="py-2.5 px-3 font-bold text-white">{job.records_processed}</td>
                    <td className="py-2.5 px-3 text-rose-400 truncate max-w-xs">{job.error_message || '--'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
