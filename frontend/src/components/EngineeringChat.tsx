import React, { useState } from 'react';
import { AgentResponse, AgentStep } from '../types';
import { Send, Sparkles, CheckCircle2, ChevronRight, AlertTriangle, Calculator, FileCheck, Layers } from 'lucide-react';

interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  response?: AgentResponse;
  timestamp: string;
}

interface EngineeringChatProps {
  messages: ChatMessage[];
  onSendMessage: (prompt: string) => Promise<void>;
  loading: boolean;
}

export const EngineeringChat: React.FC<EngineeringChatProps> = ({
  messages,
  onSendMessage,
  loading,
}) => {
  const [inputPrompt, setInputPrompt] = useState('');

  const quickPrompts = [
    'Design a motor mounting bracket with four mounting holes, rounded corners, and 10 mm plate thickness.',
    'Increase length to 150 mm.',
    'Add 3 mm fillets to all outer corners.',
    'Check if the bracket is suitable for Bambu Lab X1C 3D printing.',
    'Export STEP and STL files.',
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputPrompt.trim() || loading) return;
    onSendMessage(inputPrompt);
    setInputPrompt('');
  };

  return (
    <div className="flex flex-col h-full bg-studio-900/60 border border-slate-800 rounded-2xl overflow-hidden glass-panel">
      {/* Panel Header */}
      <div className="px-5 py-3.5 border-b border-slate-800 bg-studio-950/70 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-studio-accent" />
          <h2 className="text-xs font-bold uppercase tracking-wider text-white">
            Lead Engineering Design Manager
          </h2>
        </div>
        <span className="text-[11px] font-mono text-slate-400">Autonomous AI Agent</span>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-5 overflow-y-auto space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-400">
            <div className="w-14 h-14 rounded-2xl bg-studio-accent/10 border border-studio-accent/30 flex items-center justify-center mb-4">
              <Sparkles className="w-7 h-7 text-studio-accent" />
            </div>
            <h3 className="text-base font-semibold text-white">AI Robotics Engineering Studio</h3>
            <p className="text-xs text-slate-400 max-w-sm mt-1">
              Instruct the agent in natural language. It will select engineering skills, calculate mechanics, and execute real parametric CAD operations.
            </p>
            {/* Quick Prompts */}
            <div className="mt-6 flex flex-wrap gap-2 justify-center max-w-lg">
              {quickPrompts.map((p, i) => (
                <button
                  key={i}
                  onClick={() => onSendMessage(p)}
                  className="px-3 py-1.5 rounded-lg bg-studio-950/80 border border-slate-800 text-xs text-slate-300 hover:border-studio-accent hover:text-white transition-all text-left"
                >
                  "{p}"
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
            >
              {/* Message Bubble */}
              <div
                className={`max-w-[88%] rounded-2xl p-4 text-xs ${
                  msg.sender === 'user'
                    ? 'bg-studio-accent text-studio-950 font-medium'
                    : 'bg-studio-950 border border-slate-800 text-slate-200'
                }`}
              >
                {msg.sender === 'user' ? (
                  <p className="leading-relaxed">{msg.text}</p>
                ) : (
                  <div className="space-y-3">
                    {/* Active Skill Badge */}
                    {msg.response?.active_skill && (
                      <div className="flex items-center space-x-2 pb-2 border-b border-slate-800/80">
                        <span className="px-2.5 py-0.5 rounded-full bg-studio-accent/10 border border-studio-accent/30 text-studio-accent font-mono text-[10px] font-semibold">
                          SKILL: {msg.response.active_skill.toUpperCase()}
                        </span>
                        {msg.response.skill_evaluation?.status && (
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              msg.response.skill_evaluation.status === 'PASS'
                                ? 'bg-emerald-500/10 text-emerald-400'
                                : 'bg-amber-500/10 text-amber-400'
                            }`}
                          >
                            {msg.response.skill_evaluation.status}
                          </span>
                        )}
                      </div>
                    )}

                    {/* Reasoning Execution Steps */}
                    {msg.response?.steps && msg.response.steps.length > 0 && (
                      <div className="space-y-1.5 pt-1">
                        <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
                          Execution Pipeline:
                        </span>
                        {msg.response.steps.map((st: AgentStep) => (
                          <div
                            key={st.step_number}
                            className="flex items-start space-x-2 text-[11px] bg-studio-900/80 p-2 rounded-lg border border-slate-800/60"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5 text-studio-accent shrink-0 mt-0.5" />
                            <div>
                              <span className="font-semibold text-white">{st.name}: </span>
                              <span className="text-slate-300">{st.details}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Reply Text */}
                    <div className="whitespace-pre-line leading-relaxed text-slate-200 pt-1 border-t border-slate-800/60">
                      {msg.text}
                    </div>

                    {/* Mass & Volume Footnote */}
                    {msg.response?.mass_properties && (
                      <div className="grid grid-cols-3 gap-2 p-2.5 rounded-lg bg-studio-900/60 border border-slate-800 text-[11px] font-mono">
                        <div>
                          <span className="text-slate-500 block">Mass:</span>
                          <span className="text-white font-semibold">{msg.response.mass_properties.mass_g} g</span>
                        </div>
                        <div>
                          <span className="text-slate-500 block">Volume:</span>
                          <span className="text-white font-semibold">{msg.response.mass_properties.volume_mm3.toLocaleString()} mm³</span>
                        </div>
                        <div>
                          <span className="text-slate-500 block">Material:</span>
                          <span className="text-studio-accent font-semibold">{msg.response.mass_properties.material_name}</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
              <span className="text-[10px] text-slate-500 mt-1 px-1">{msg.timestamp}</span>
            </div>
          ))
        )}

        {loading && (
          <div className="flex items-center space-x-3 p-4 rounded-xl bg-studio-950 border border-slate-800 text-xs text-studio-accent max-w-[280px]">
            <Sparkles className="w-4 h-4 animate-spin" />
            <span>AI Lead Agent synthesizing CAD operations...</span>
          </div>
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-slate-800 bg-studio-950/80">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
            placeholder="Instruct the engineering agent (e.g. 'Design a mounting bracket 100x60x10 mm with 4 holes')..."
            disabled={loading}
            className="flex-1 bg-studio-900 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-studio-accent transition-colors disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !inputPrompt.trim()}
            className="px-4 py-2.5 rounded-xl bg-studio-accent text-studio-950 font-bold text-xs hover:bg-cyan-300 transition-colors disabled:opacity-40 flex items-center gap-1.5 shrink-0 shadow-lg shadow-cyan-500/20"
          >
            <span>Send</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </form>
    </div>
  );
};
