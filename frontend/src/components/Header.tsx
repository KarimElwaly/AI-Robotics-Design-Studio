import React from 'react';
import { ConnectionStatus } from '../types';
import { Cpu, Layers, CheckCircle2, AlertTriangle, ShieldCheck, RefreshCw, Radio } from 'lucide-react';

interface HeaderProps {
  status: ConnectionStatus | null;
  onOpenConnectionModal: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  status,
  onOpenConnectionModal,
  activeTab,
  setActiveTab,
}) => {
  const isConnected = status?.connected ?? false;
  const isMock = status?.active_version?.is_mock ?? false;
  const versionName = status?.active_version?.version_name ?? 'Detecting...';
  const activeDoc = status?.active_document || 'No Document';

  return (
    <header className="h-16 border-b border-slate-800 glass-panel px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand & Title */}
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-studio-accent to-blue-600 flex items-center justify-center glow-accent">
          <Cpu className="w-6 h-6 text-studio-950" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
              AI ROBOTICS DESIGN STUDIO
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-studio-accent/10 border border-studio-accent/30 text-studio-accent">
                SW 2024 + 2026
              </span>
            </h1>
          </div>
          <p className="text-xs text-slate-400">Autonomous Engineering & Parametric CAD Intelligence</p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav className="flex items-center space-x-1 bg-studio-900 p-1 rounded-xl border border-slate-800">
        {[
          { id: 'workbench', label: 'CAD Workbench' },
          { id: 'skills', label: 'Engineering Skills' },
          { id: 'validation', label: 'Validation' },
          { id: 'library', label: 'Project Library' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-studio-accent text-studio-950 font-semibold shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* SOLIDWORKS Connection Hub Status Bar */}
      <div className="flex items-center space-x-3">
        {/* Active Document Pill */}
        <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-studio-900 border border-slate-800 text-xs">
          <Layers className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-400">Active Doc:</span>
          <span className="font-mono text-slate-200 truncate max-w-[140px]">{activeDoc}</span>
        </div>

        {/* Connection Status Button */}
        <button
          onClick={onOpenConnectionModal}
          className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${
            isConnected
              ? isMock
                ? 'bg-amber-950/30 border-amber-500/40 text-amber-300 hover:bg-amber-900/40'
                : 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300 hover:bg-emerald-900/40'
              : 'bg-rose-950/30 border-rose-500/40 text-rose-300 hover:bg-rose-900/40'
          }`}
        >
          <span className="relative flex h-2 w-2">
            <span
              className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                isConnected ? (isMock ? 'bg-amber-400' : 'bg-emerald-400') : 'bg-rose-400'
              }`}
            />
            <span
              className={`relative inline-flex rounded-full h-2 w-2 ${
                isConnected ? (isMock ? 'bg-amber-500' : 'bg-emerald-500') : 'bg-rose-500'
              }`}
            />
          </span>
          <span className="font-mono">{versionName}</span>
          <Radio className="w-3.5 h-3.5 opacity-70" />
        </button>
      </div>
    </header>
  );
};
