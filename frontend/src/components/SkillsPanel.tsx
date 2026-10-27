import React, { useState } from 'react';
import { Cpu, ShieldCheck, Printer, Paintbrush, Wrench, Play, CheckCircle2 } from 'lucide-react';

export const SkillsPanel: React.FC = () => {
  const [evaluating, setEvaluating] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);

  const skills = [
    {
      id: 'mechanical',
      name: 'Mechanical Design Engineer',
      icon: Wrench,
      accent: 'text-blue-400',
      description: 'Calculates bending stress, torsion, deflection, and Factor of Safety (FoS) per Shigley standards. Validates motor brackets and fastener spacing.',
      formulas: ['σ = (M · y) / I', 'τ = (T · r) / J', 'σ_v = √(σ² + 3τ²)', 'FoS = S_y / σ_v'],
    },
    {
      id: 'industrial',
      name: 'Industrial Product Designer',
      icon: Paintbrush,
      accent: 'text-purple-400',
      description: 'Establishes aviation styling, CMF palettes (RAL 9016 Traffic White + RAL 1036 Satin Gold), G2 surface blends, and exterior panel seam architecture.',
      formulas: ['Aviation White: RAL 9016 (#F6F6F6)', 'Metallic Gold: RAL 1036 (#8F7242)', 'Reveal Gap: 1.5 mm'],
    },
    {
      id: 'robotics',
      name: 'Robotics Systems Engineer',
      icon: Cpu,
      accent: 'text-studio-accent',
      description: 'Architects 3-wheel mobile robot chassis (2 drive wheels, 1 caster), motor torque/power sizing, battery packaging, and CG tip-over stability triangles.',
      formulas: ['T_wheel = (F_roll + F_incline + F_accel) · r / 2', 'a_tip = g · (b / h_cg)'],
    },
    {
      id: 'additive',
      name: 'Additive Manufacturing Engineer',
      icon: Printer,
      accent: 'text-amber-400',
      description: 'Bambu Lab X1C / X1E validation (256³ mm envelope), material profiles (PLA, PETG-CF, ABS-GF, PAHT-CF), heat-set brass inserts, and part splitting.',
      formulas: ['Envelope: 256 x 256 x 256 mm', 'M3 Insert: ⌀4.0 mm x 5.7 mm', 'Min Wall: 1.6 mm'],
    },
    {
      id: 'validation',
      name: 'Engineering Validation Specialist',
      icon: ShieldCheck,
      accent: 'text-emerald-400',
      description: 'Continuous quality scorecard: verifies 0 rebuild errors, manifold solid bounding box, fastener edge distances, mass accuracy, and structural safety margins.',
      formulas: ['Rebuild Errors == 0', 'Edge Margin >= 1.5 · d_hole', 'FoS >= 2.0'],
    },
  ];

  const handleTestSkill = async (skillId: string) => {
    setEvaluating(skillId);
    try {
      const res = await fetch('/api/skills/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          skill_name: skillId,
          request: 'Execute automated verification and parameter sizing',
        }),
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setEvaluating(null);
    }
  };

  return (
    <div className="h-full space-y-6 overflow-y-auto pr-1">
      <div>
        <h2 className="text-lg font-bold text-white">Engineering Skills Studio</h2>
        <p className="text-xs text-slate-400">
          The 5 specialized agent skill modules coordinating physical formulas, CAD rules, and manufacturing constraints.
        </p>
      </div>

      {/* Grid of Skill Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {skills.map((skill) => {
          const Icon = skill.icon;
          return (
            <div
              key={skill.id}
              className="p-5 rounded-2xl bg-studio-900/60 border border-slate-800 glass-panel flex flex-col justify-between hover:border-slate-700 transition-all"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className={`w-10 h-10 rounded-xl bg-studio-950 border border-slate-800 flex items-center justify-center ${skill.accent}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    ACTIVE
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white">{skill.name}</h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">{skill.description}</p>

                {/* Mathematical formulas pill tags */}
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {skill.formulas.map((f, i) => (
                    <span
                      key={i}
                      className="text-[10px] font-mono px-2 py-0.5 rounded bg-studio-950 text-slate-300 border border-slate-800"
                    >
                      {f}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center justify-between">
                <span className="text-[11px] text-slate-500">Autonomous Tool Access</span>
                <button
                  onClick={() => handleTestSkill(skill.id)}
                  disabled={evaluating === skill.id}
                  className="px-3 py-1.5 rounded-lg bg-studio-950 border border-slate-700 hover:border-studio-accent text-slate-200 text-xs font-medium flex items-center gap-1.5 transition-colors disabled:opacity-50"
                >
                  <Play className="w-3 h-3 text-studio-accent" />
                  <span>{evaluating === skill.id ? 'Running...' : 'Run Test'}</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Evaluation Output Drawer */}
      {result && (
        <div className="p-5 rounded-2xl bg-studio-900/80 border border-slate-700 glass-panel animate-fade-in">
          <div className="flex items-center space-x-2 mb-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-white">
              Skill Evaluation Result: {result.skill_name}
            </h3>
          </div>
          <p className="text-xs text-slate-300 mb-3">{result.summary}</p>
          <pre className="p-3 rounded-xl bg-studio-950 border border-slate-800 text-[11px] font-mono text-studio-accent overflow-x-auto">
            {JSON.stringify(result.calculations, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
