import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { ConnectionModal } from './components/ConnectionModal';
import { EngineeringChat } from './components/EngineeringChat';
import { CadWorkspace } from './components/CadWorkspace';
import { SkillsPanel } from './components/SkillsPanel';
import { ValidationDashboard } from './components/ValidationDashboard';
import { ProjectLibrary } from './components/ProjectLibrary';
import { ConnectionStatus, FeatureInfo, DimensionInfo, MassProperties, VersionInfo, AgentResponse } from './types';

interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  response?: AgentResponse;
  timestamp: string;
}

export function App() {
  const [activeTab, setActiveTab] = useState<string>('workbench');
  const [isConnModalOpen, setIsConnModalOpen] = useState<boolean>(false);
  const [status, setStatus] = useState<ConnectionStatus | null>(null);

  // Model Inspection State
  const [activeDoc, setActiveDoc] = useState<string>('Part_2024_1');
  const [features, setFeatures] = useState<FeatureInfo[]>([]);
  const [dimensions, setDimensions] = useState<DimensionInfo[]>([]);
  const [massProps, setMassProps] = useState<MassProperties | null>(null);
  const [versionInfo, setVersionInfo] = useState<VersionInfo | null>(null);

  // Chat State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatLoading, setChatLoading] = useState<boolean>(false);

  // Fetch CAD Status and Model Info
  const refreshStatus = async () => {
    try {
      const res = await fetch('/api/cad/status');
      const data: ConnectionStatus = await res.json();
      setStatus(data);
      if (data.active_version) {
        setVersionInfo(data.active_version);
      }
    } catch (e) {
      console.error('Error fetching CAD status:', e);
    }
  };

  const refreshModelInfo = async () => {
    try {
      const res = await fetch('/api/cad/model-info');
      const data = await res.json();
      setActiveDoc(data.active_document || 'Part_2024_1');
      setFeatures(data.features || []);
      setDimensions(data.dimensions || []);
      setMassProps(data.mass_properties || null);
    } catch (e) {
      console.error('Error fetching model info:', e);
    }
  };

  useEffect(() => {
    refreshStatus();
    refreshModelInfo();
  }, []);

  // Handle Mode Change
  const handleConnectMode = async (mode: string) => {
    try {
      const res = await fetch('/api/cad/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode }),
      });
      const data = await res.json();
      setStatus(data.status);
      if (data.status.active_version) {
        setVersionInfo(data.status.active_version);
      }
      await refreshModelInfo();
      setIsConnModalOpen(false);
    } catch (e) {
      console.error(e);
    }
  };

  const handleDisconnect = async () => {
    try {
      await fetch('/api/cad/disconnect', { method: 'POST' });
      await refreshStatus();
      setIsConnModalOpen(false);
    } catch (e) {
      console.error(e);
    }
  };

  // Chat Handling
  const handleSendMessage = async (prompt: string) => {
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: prompt,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, userMsg]);
    setChatLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });
      const data: AgentResponse = await res.json();

      const agentMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: data.reply,
        response: data,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, agentMsg]);

      // Update model info
      await refreshModelInfo();
      await refreshStatus();
    } catch (e) {
      console.error('Chat error:', e);
    } finally {
      setChatLoading(false);
    }
  };

  // Modify Dimension directly from CAD Inspector
  const handleModifyDimension = async (dimName: string, value: number) => {
    try {
      await fetch('/api/cad/modify-dimension', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dimension_name: dimName, value_mm: value }),
      });
      await refreshModelInfo();
    } catch (e) {
      console.error(e);
    }
  };

  // Rebuild
  const handleRebuild = async () => {
    try {
      await fetch('/api/cad/rebuild', { method: 'POST' });
      await refreshModelInfo();
    } catch (e) {
      console.error(e);
    }
  };

  // Export STEP or STL
  const handleExport = async (format: 'STEP' | 'STL') => {
    try {
      await handleSendMessage(`Export ${format} file to projects folder.`);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-studio-950 text-slate-100">
      {/* Top Application Header */}
      <Header
        status={status}
        onOpenConnectionModal={() => setIsConnModalOpen(true)}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {/* Main Workspace Body */}
      <main className="flex-1 p-5 overflow-hidden">
        {activeTab === 'workbench' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 h-full">
            {/* Left Column: Natural-Language Engineering Chat (5 cols) */}
            <div className="lg:col-span-5 h-full">
              <EngineeringChat
                messages={messages}
                onSendMessage={handleSendMessage}
                loading={chatLoading}
              />
            </div>

            {/* Right Column: CAD Viewport & Inspector (7 cols) */}
            <div className="lg:col-span-7 h-full overflow-y-auto">
              <CadWorkspace
                activeDoc={activeDoc}
                features={features}
                dimensions={dimensions}
                massProps={massProps}
                versionInfo={versionInfo}
                onModifyDimension={handleModifyDimension}
                onRebuild={handleRebuild}
                onExport={handleExport}
              />
            </div>
          </div>
        )}

        {activeTab === 'skills' && <SkillsPanel />}

        {activeTab === 'validation' && <ValidationDashboard />}

        {activeTab === 'library' && <ProjectLibrary />}
      </main>

      {/* SOLIDWORKS Connection Hub Modal */}
      <ConnectionModal
        isOpen={isConnModalOpen}
        onClose={() => setIsConnModalOpen(false)}
        status={status}
        onConnectMode={handleConnectMode}
        onDisconnect={handleDisconnect}
        onRefresh={refreshStatus}
      />
    </div>
  );
}

export default App;
