import React, { useState } from 'react';
import { DimensionInfo, FeatureInfo, MassProperties, VersionInfo } from '../types';
import { Box, Layers, Download, RefreshCw, CheckCircle2, Sliders, Scale, FileCode, Check } from 'lucide-react';

interface CadWorkspaceProps {
  activeDoc: string;
  features: FeatureInfo[];
  dimensions: DimensionInfo[];
  massProps: MassProperties | null;
  versionInfo: VersionInfo | null;
  onModifyDimension: (dimName: string, value: number) => Promise<void>;
  onRebuild: () => Promise<void>;
  onExport: (format: 'STEP' | 'STL') => Promise<void>;
}

export const CadWorkspace: React.FC<CadWorkspaceProps> = ({
  activeDoc,
  features,
  dimensions,
  massProps,
  versionInfo,
  onModifyDimension,
  onRebuild,
  onExport,
}) => {
  const [editingDim, setEditingDim] = useState<string | null>(null);
  const [dimVal, setDimVal] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [exportedMsg, setExportedMsg] = useState<string | null>(null);

  const handleUpdateDim = async (name: string) => {
    setLoading(true);
    try {
      await onModifyDimension(name, dimVal);
      setEditingDim(null);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (fmt: 'STEP' | 'STL') => {
    setLoading(true);
    try {
      await onExport(fmt);
      setExportedMsg(`Exported ${fmt} to projects folder!`);
      setTimeout(() => setExportedMsg(null), 3500);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Top CAD Status & Controls Bar */}
      <div className="p-4 rounded-2xl bg-studio-900/60 border border-slate-800 glass-panel flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-studio-accent/10 border border-studio-accent/30 flex items-center justify-center">
            <Box className="w-5 h-5 text-studio-accent" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-white font-mono">{activeDoc || 'Parametric Part Model'}</h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> REBUILD CLEAN (0 ERRORS)
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Connected: {versionInfo?.version_name || 'SOLIDWORKS Engine'}
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-2">
          {exportedMsg && (
            <span className="text-xs text-emerald-400 font-mono animate-fade-in flex items-center gap-1">
              <Check className="w-3.5 h-3.5" /> {exportedMsg}
            </span>
          )}
          <button
            onClick={onRebuild}
            disabled={loading}
            className="px-3 py-1.5 rounded-xl border border-slate-700 bg-studio-950 text-slate-300 hover:text-white text-xs font-medium flex items-center gap-1.5 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Rebuild
          </button>
          <button
            onClick={() => handleExport('STEP')}
            disabled={loading}
            className="px-3 py-1.5 rounded-xl bg-studio-950 border border-slate-700 hover:border-studio-accent text-slate-300 hover:text-white text-xs font-mono flex items-center gap-1.5 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-studio-accent" /> STEP
          </button>
          <button
            onClick={() => handleExport('STL')}
            disabled={loading}
            className="px-3 py-1.5 rounded-xl bg-studio-950 border border-slate-700 hover:border-amber-400 text-slate-300 hover:text-white text-xs font-mono flex items-center gap-1.5 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-amber-400" /> STL
          </button>
        </div>
      </div>

      {/* Grid: Viewport & Feature Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 flex-1 min-h-0">
        {/* Viewport Preview (2 cols) */}
        <div className="lg:col-span-2 rounded-2xl bg-studio-900/60 border border-slate-800 glass-panel overflow-hidden flex flex-col">
          <div className="px-4 py-2.5 border-b border-slate-800/80 bg-studio-950/80 flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400 uppercase">Parametric Model Viewport</span>
            <span className="text-[11px] font-mono text-studio-accent">ISO VIEW • WIREFRAME OVERLAY</span>
          </div>

          {/* Interactive Visual Canvas Container */}
          <div className="flex-1 bg-gradient-to-b from-studio-950 to-studio-900 flex items-center justify-center p-6 relative">
            {/* High-Tech CAD Wireframe SVG Preview */}
            <svg viewBox="0 0 700 450" className="w-full h-full max-h-[380px] drop-shadow-2xl">
              <defs>
                <linearGradient id="gridGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#00e5ff" stopOpacity="0.08" />
                  <stop offset="100%" stopColor="#070a0f" stopOpacity="0.8" />
                </linearGradient>
                <linearGradient id="plateGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#1e293b" stopOpacity="0.9" />
                  <stop offset="100%" stopColor="#0f172a" stopOpacity="0.95" />
                </linearGradient>
              </defs>

              {/* Grid Background */}
              <pattern id="cadGrid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
              </pattern>
              <rect width="100%" height="100%" fill="url(#cadGrid)" />

              {/* Extruded 3D Plate Isometric Mock */}
              {/* Lower Shadow Plate */}
              <polygon points="120,290 520,290 580,210 180,210" fill="none" stroke="#00e5ff" strokeWidth="1.5" strokeDasharray="4 4" opacity="0.4" />
              {/* Extrusion Vertical Edges */}
              <line x1="120" y1="290" x2="120" y2="250" stroke="#00e5ff" strokeWidth="2" />
              <line x1="520" y1="290" x2="520" y2="250" stroke="#00e5ff" strokeWidth="2" />
              <line x1="580" y1="210" x2="580" y2="170" stroke="#00e5ff" strokeWidth="2" />
              <line x1="180" y1="210" x2="180" y2="170" stroke="#00e5ff" strokeWidth="2" />

              {/* Top Face Plate */}
              <polygon points="120,250 520,250 580,170 180,170" fill="url(#plateGrad)" stroke="#00e5ff" strokeWidth="2.5" />

              {/* Four Mounting Holes on Top Face */}
              <ellipse cx="170" cy="235" rx="14" ry="8" fill="#070a0f" stroke="#00e5ff" strokeWidth="1.5" />
              <ellipse cx="470" cy="235" rx="14" ry="8" fill="#070a0f" stroke="#00e5ff" strokeWidth="1.5" />
              <ellipse cx="230" cy="185" rx="14" ry="8" fill="#070a0f" stroke="#00e5ff" strokeWidth="1.5" />
              <ellipse cx="530" cy="185" rx="14" ry="8" fill="#070a0f" stroke="#00e5ff" strokeWidth="1.5" />

              {/* Dimension Annotations */}
              {/* Length D1 */}
              <line x1="120" y1="315" x2="520" y2="315" stroke="#eab308" strokeWidth="1.5" markerStart="url(#arrow)" markerEnd="url(#arrow)" />
              <line x1="120" y1="290" x2="120" y2="325" stroke="#eab308" strokeWidth="1" strokeDasharray="2 2" />
              <line x1="520" y1="290" x2="520" y2="325" stroke="#eab308" strokeWidth="1" strokeDasharray="2 2" />
              <text x="320" y="335" fill="#eab308" fontSize="13" fontFamily="monospace" textAnchor="middle" fontWeight="bold">
                Length: {dimensions.find(d => d.name.includes('D1'))?.value_mm ?? 100.0} mm
              </text>

              {/* Thickness Extrusion Height */}
              <line x1="95" y1="250" x2="95" y2="290" stroke="#00e5ff" strokeWidth="1.5" />
              <text x="85" y="275" fill="#00e5ff" fontSize="11" fontFamily="monospace" textAnchor="end">
                10 mm
              </text>

              {/* Corner Fillets */}
              <text x="595" y="170" fill="#a855f7" fontSize="11" fontFamily="monospace">
                R3.0 mm
              </text>
            </svg>

            {/* Viewport Floating Info */}
            <div className="absolute bottom-4 left-4 p-2.5 rounded-xl bg-studio-950/80 border border-slate-800 text-[11px] font-mono text-slate-400 backdrop-blur-md">
              <span className="text-studio-accent font-semibold">Coordinate System: </span> Front Plane (SI units, mm active)
            </div>
          </div>
        </div>

        {/* Right Column: Dimensions & Feature Tree */}
        <div className="space-y-4 flex flex-col">
          {/* Driving Dimensions Card */}
          <div className="p-4 rounded-2xl bg-studio-900/60 border border-slate-800 glass-panel">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Sliders className="w-4 h-4 text-studio-gold" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">Driving Dimensions</h3>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">Click to edit</span>
            </div>

            <div className="space-y-2">
              {dimensions.length === 0 ? (
                <p className="text-xs text-slate-500 py-2">No active dimensions.</p>
              ) : (
                dimensions.map((dim) => (
                  <div
                    key={dim.name}
                    className="p-2.5 rounded-xl bg-studio-950 border border-slate-800/80 flex items-center justify-between text-xs"
                  >
                    <div>
                      <p className="font-mono text-slate-300 font-medium">{dim.name}</p>
                      <p className="text-[10px] text-slate-500">{dim.full_name || dim.name}</p>
                    </div>

                    {editingDim === dim.name ? (
                      <div className="flex items-center space-x-1">
                        <input
                          type="number"
                          value={dimVal}
                          onChange={(e) => setDimVal(parseFloat(e.target.value) || 0)}
                          className="w-20 px-2 py-1 bg-studio-900 border border-studio-accent rounded text-xs text-white font-mono"
                          autoFocus
                        />
                        <button
                          onClick={() => handleUpdateDim(dim.name)}
                          className="p-1 rounded bg-studio-accent text-studio-950 font-bold"
                        >
                          <Check className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => {
                          setEditingDim(dim.name);
                          setDimVal(dim.value_mm);
                        }}
                        className="font-mono font-bold text-studio-gold hover:text-yellow-300 px-2 py-1 rounded bg-yellow-500/10 border border-yellow-500/20"
                      >
                        {dim.value_mm} mm
                      </button>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Mass Properties Card */}
          {massProps && (
            <div className="p-4 rounded-2xl bg-studio-900/60 border border-slate-800 glass-panel">
              <div className="flex items-center space-x-2 mb-3">
                <Scale className="w-4 h-4 text-studio-accent" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">Mass Properties</h3>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-2 rounded-lg bg-studio-950 border border-slate-800/60">
                  <span className="text-slate-500 text-[10px] block">Total Mass:</span>
                  <span className="text-white font-semibold">{massProps.mass_g} g</span>
                </div>
                <div className="p-2 rounded-lg bg-studio-950 border border-slate-800/60">
                  <span className="text-slate-500 text-[10px] block">Net Volume:</span>
                  <span className="text-white font-semibold">{massProps.volume_mm3.toLocaleString()} mm³</span>
                </div>
                <div className="p-2 rounded-lg bg-studio-950 border border-slate-800/60">
                  <span className="text-slate-500 text-[10px] block">Material:</span>
                  <span className="text-studio-accent font-semibold truncate block">{massProps.material_name}</span>
                </div>
                <div className="p-2 rounded-lg bg-studio-950 border border-slate-800/60">
                  <span className="text-slate-500 text-[10px] block">Center of Gravity:</span>
                  <span className="text-slate-300 text-[10px]">({massProps.center_of_gravity_mm[0]}, {massProps.center_of_gravity_mm[1]}, {massProps.center_of_gravity_mm[2]})</span>
                </div>
              </div>
            </div>
          )}

          {/* Feature Tree */}
          <div className="p-4 rounded-2xl bg-studio-900/60 border border-slate-800 glass-panel flex-1">
            <div className="flex items-center space-x-2 mb-3">
              <Layers className="w-4 h-4 text-slate-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-white">FeatureManager Tree</h3>
            </div>
            <div className="space-y-1.5 max-h-[160px] overflow-y-auto">
              {features.map((feat, i) => (
                <div
                  key={i}
                  className="px-2.5 py-1.5 rounded-lg bg-studio-950/60 border border-slate-800/40 text-xs font-mono flex items-center justify-between text-slate-300"
                >
                  <span>{feat.name}</span>
                  <span className="text-[10px] text-slate-500">{feat.type_name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
