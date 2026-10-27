import React, { useState, useEffect } from 'react';
import { Folder, FileCode, Download, RefreshCw, FileText, Image, Box } from 'lucide-react';

interface ProjectFile {
  filename: string;
  relative_path: string;
  size_bytes: number;
  extension: string;
}

export const ProjectLibrary: React.FC = () => {
  const [files, setFiles] = useState<ProjectFile[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchFiles = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/projects');
      const data = await res.json();
      setFiles(data.files || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const getFileIcon = (ext: string) => {
    if (ext === '.sldprt' || ext === '.sldasm') return <Box className="w-4 h-4 text-studio-accent" />;
    if (ext === '.step' || ext === '.stp') return <FileCode className="w-4 h-4 text-studio-gold" />;
    if (ext === '.stl') return <FileCode className="w-4 h-4 text-amber-400" />;
    if (ext === '.png' || ext === '.jpg') return <Image className="w-4 h-4 text-purple-400" />;
    return <FileText className="w-4 h-4 text-slate-400" />;
  };

  return (
    <div className="h-full space-y-6 overflow-y-auto pr-1">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white">Project CAD Library & Exports</h2>
          <p className="text-xs text-slate-400">
            Native SLDPRT models, neutral STEP/STL exchange files, and design revisions.
          </p>
        </div>
        <button
          onClick={fetchFiles}
          disabled={loading}
          className="px-3.5 py-1.5 rounded-xl bg-studio-950 border border-slate-700 hover:border-studio-accent text-slate-300 text-xs font-medium flex items-center gap-1.5 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Refresh Files
        </button>
      </div>

      {/* File List Grid */}
      <div className="rounded-2xl bg-studio-900/60 border border-slate-800 glass-panel overflow-hidden">
        <div className="px-5 py-3.5 border-b border-slate-800 bg-studio-950 flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Workspace Files ({files.length})
          </span>
          <span className="text-[11px] font-mono text-slate-500">Directory: d:\cad\projects\</span>
        </div>

        {files.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-xs">
            <Folder className="w-8 h-8 mx-auto text-slate-600 mb-2 opacity-50" />
            No files in project library yet. Run a CAD generation prompt or export to populate.
          </div>
        ) : (
          <div className="divide-y divide-slate-800/80">
            {files.map((f, i) => (
              <div
                key={i}
                className="p-4 flex items-center justify-between hover:bg-slate-800/20 transition-colors text-xs"
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-xl bg-studio-950 border border-slate-800">
                    {getFileIcon(f.extension)}
                  </div>
                  <div>
                    <p className="font-mono text-white font-semibold">{f.filename}</p>
                    <p className="text-[11px] text-slate-500">{f.relative_path}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <span className="text-slate-400 font-mono text-[11px]">
                    {(f.size_bytes / 1024).toFixed(1)} KB
                  </span>
                  <a
                    href={`/files/${f.relative_path}`}
                    download={f.filename}
                    className="p-2 rounded-xl bg-studio-950 border border-slate-700 hover:border-studio-accent text-studio-accent transition-colors"
                    title="Download file"
                  >
                    <Download className="w-4 h-4" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
