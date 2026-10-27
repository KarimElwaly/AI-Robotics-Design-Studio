import React, { useState } from 'react';
import { ConnectionStatus } from '../types';
import { X, CheckCircle2, AlertCircle, RefreshCw, Radio, HardDrive, Cpu, Power } from 'lucide-react';

interface ConnectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  status: ConnectionStatus | null;
  onConnectMode: (mode: string) => Promise<void>;
  onDisconnect: () => Promise<void>;
  onRefresh: () => Promise<void>;
}

export const ConnectionModal: React.FC<ConnectionModalProps> = ({
  isOpen,
  onClose,
  status,
  onConnectMode,
  onDisconnect,
  onRefresh,
}) => {
  const [loading, setLoading] = useState(false);
  const [selectedMode, setSelectedMode] = useState<string>(status?.mode || 'mock');

  if (!isOpen) return null;

  const handleApply = async () => {
    setLoading(true);
    try {
      await onConnectMode(selectedMode);
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    setLoading(true);
    try {
      await onDisconnect();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-studio-900 border border-slate-700/60 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <Radio className="w-5 h-5 text-studio-accent" />
            <h2 className="text-base font-semibold text-white">SOLIDWORKS Connection Hub</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5">
          {/* Active Status Banner */}
          <div className="p-4 rounded-xl bg-studio-950 border border-slate-800 flex items-start justify-between">
            <div>
              <span className="text-xs text-slate-400">Current CAD Adapter</span>
              <p className="text-sm font-semibold text-white mt-0.5">
                {status?.active_version?.version_name || 'Disconnected'}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {status?.active_version?.is_mock
                  ? 'Simulated in-memory CAD engine for headless CI/CD & rapid development.'
                  : 'Live Windows COM process binding via pywin32 STA worker.'}
              </p>
            </div>
            <span
              className={`px-2.5 py-1 rounded-full text-[11px] font-mono font-medium ${
                status?.connected
                  ? status?.active_version?.is_mock
                    ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                    : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                  : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
              }`}
            >
              {status?.connected ? (status?.active_version?.is_mock ? 'SIMULATED' : 'LIVE COM') : 'OFFLINE'}
            </span>
          </div>

          {/* Mode Selector */}
          <div>
            <label className="text-xs font-medium text-slate-300 block mb-2">
              Select Target Installation:
            </label>
            <div className="grid grid-cols-2 gap-2.5">
              {[
                { id: 'auto', label: 'Auto Detect', desc: 'Prioritize running 2026, then 2024' },
                { id: '2026', label: 'SOLIDWORKS 2026', desc: 'Target Major 34 COM dispatch' },
                { id: '2024', label: 'SOLIDWORKS 2024', desc: 'Target Major 32 COM dispatch' },
                { id: 'mock', label: 'Mock Engine', desc: 'Simulated CAD with real STEP/STL' },
              ].map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => setSelectedMode(mode.id)}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    selectedMode === mode.id
                      ? 'border-studio-accent bg-studio-accent/10 text-white'
                      : 'border-slate-800 bg-studio-950/60 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <p className="text-xs font-semibold text-slate-200">{mode.label}</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">{mode.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Detected Installations on System */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-medium text-slate-300">
                Detected System Installations:
              </label>
              <button
                onClick={onRefresh}
                className="text-xs text-studio-accent hover:underline flex items-center gap-1"
              >
                <RefreshCw className="w-3 h-3" /> Rescan Registry
              </button>
            </div>
            <div className="space-y-2">
              {status?.detected_installations && status.detected_installations.length > 0 ? (
                status.detected_installations.map((inst, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-studio-950/80 border border-slate-800/80 flex items-center justify-between text-xs"
                  >
                    <div className="flex items-center space-x-2.5">
                      <HardDrive className="w-4 h-4 text-slate-400" />
                      <div>
                        <p className="font-semibold text-slate-200">
                          SOLIDWORKS {inst.year} (Major {inst.major_version})
                        </p>
                        <p className="text-[11px] text-slate-500 truncate max-w-[280px]">
                          {inst.executable_path || inst.install_path || 'Registry registered'}
                        </p>
                      </div>
                    </div>
                    {inst.is_running ? (
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px]">
                        RUNNING (PID {inst.process_id})
                      </span>
                    ) : (
                      <span className="text-slate-500 text-[11px]">Installed</span>
                    )}
                  </div>
                ))
              ) : (
                <div className="p-3 rounded-xl bg-studio-950/40 border border-slate-800/50 text-xs text-slate-400 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>No live SOLIDWORKS processes found in current registry. Mock Adapter active for tests.</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-studio-950 flex items-center justify-between">
          <button
            onClick={handleDisconnect}
            disabled={loading || !status?.connected}
            className="px-3.5 py-2 rounded-xl border border-rose-500/30 text-rose-400 hover:bg-rose-950/30 text-xs font-medium flex items-center gap-1.5 transition-colors disabled:opacity-40"
          >
            <Power className="w-3.5 h-3.5" /> Disconnect
          </button>
          <div className="flex items-center space-x-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-slate-400 hover:text-white text-xs font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleApply}
              disabled={loading}
              className="px-5 py-2 rounded-xl bg-studio-accent text-studio-950 text-xs font-bold hover:bg-cyan-300 transition-colors shadow-lg shadow-cyan-500/20 flex items-center gap-1.5 disabled:opacity-50"
            >
              {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
              Apply Connection
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
