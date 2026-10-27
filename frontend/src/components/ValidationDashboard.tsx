import React, { useState, useEffect } from 'react';
import { ValidationCheck } from '../types';
import { ShieldCheck, CheckCircle2, AlertTriangle, XCircle, RefreshCw, Layers, Award } from 'lucide-react';

export const ValidationDashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any | null>(null);

  const fetchValidation = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/validation/run', { method: 'POST' });
      const data = await res.json();
      setReport(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchValidation();
  }, []);

  const checks: ValidationCheck[] = report?.calculations?.scorecard || [];
  const passedCount = report?.calculations?.passed_count ?? 0;
  const warningCount = report?.calculations?.warning_count ?? 0;
  const failedCount = report?.calculations?.failed_count ?? 0;

  return (
    <div className="h-full space-y-6 overflow-y-auto pr-1">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            Engineering Validation & Quality Dashboard
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              AUTOMATED AUDIT
            </span>
          </h2>
          <p className="text-xs text-slate-400">
            Real-time verification of rebuild states, geometric constraints, safety margins, and 3D printability.
          </p>
        </div>

        <button
          onClick={fetchValidation}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-studio-accent text-studio-950 text-xs font-bold hover:bg-cyan-300 transition-colors flex items-center gap-1.5 shadow-lg shadow-cyan-500/20 disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Run Full Validation Audit
        </button>
      </div>

      {/* Summary Scorecard Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-studio-900/60 border border-slate-800 glass-panel">
          <span className="text-xs text-slate-400 block mb-1">Overall Status</span>
          <div className="flex items-center space-x-2">
            <Award className="w-5 h-5 text-emerald-400" />
            <span className="text-xl font-bold font-mono text-emerald-400">
              {report?.status || 'PASS'}
            </span>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-studio-900/60 border border-slate-800 glass-panel">
          <span className="text-xs text-slate-400 block mb-1">Passed Checks</span>
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <span className="text-xl font-bold font-mono text-white">{passedCount}</span>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-studio-900/60 border border-slate-800 glass-panel">
          <span className="text-xs text-slate-400 block mb-1">Warnings / Advisories</span>
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <span className="text-xl font-bold font-mono text-white">{warningCount}</span>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-studio-900/60 border border-slate-800 glass-panel">
          <span className="text-xs text-slate-400 block mb-1">Critical Failures</span>
          <div className="flex items-center space-x-2">
            <XCircle className="w-5 h-5 text-rose-400" />
            <span className="text-xl font-bold font-mono text-white">{failedCount}</span>
          </div>
        </div>
      </div>

      {/* Detailed Check Table */}
      <div className="rounded-2xl bg-studio-900/60 border border-slate-800 glass-panel overflow-hidden">
        <div className="px-5 py-3.5 border-b border-slate-800 bg-studio-950 flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Automated Rule Check Matrix
          </span>
          <span className="text-[11px] font-mono text-slate-500">Shigley & ISO Standards</span>
        </div>

        <div className="divide-y divide-slate-800/80">
          {checks.map((c, i) => (
            <div key={i} className="p-4 flex items-center justify-between hover:bg-slate-800/20 transition-colors text-xs">
              <div className="space-y-0.5">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-white">{c.name}</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-studio-950 text-slate-400 border border-slate-800">
                    {c.category}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400">{c.details}</p>
              </div>

              <div className="flex items-center space-x-6 text-right">
                <div className="font-mono">
                  <span className="text-slate-500 text-[10px] block">Actual Value</span>
                  <span className="text-slate-200 font-semibold">{c.value}</span>
                </div>

                <div className="font-mono">
                  <span className="text-slate-500 text-[10px] block">Threshold</span>
                  <span className="text-slate-400">{c.threshold}</span>
                </div>

                <span
                  className={`px-3 py-1 rounded-full text-[10px] font-bold font-mono ${
                    c.status === 'PASS'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : c.status === 'WARNING'
                      ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                  }`}
                >
                  {c.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
