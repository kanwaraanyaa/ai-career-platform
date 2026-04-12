"use client";
import React from "react"; // Add this line

interface SelectionReportProps {
  data: any;
  onBack: () => void;
}

export default function SelectionReport({ data, onBack }: SelectionReportProps) {
  // Check if data exists to prevent crashes
  if (!data) return null;

  return (
    <div className="w-full max-w-6xl mx-auto space-y-8 animate-in fade-in zoom-in-95 duration-700 py-8">
      {/* Rest of the code remains the same */}
      <div className="bg-slate-900 rounded-[3rem] p-10 text-white shadow-2xl relative overflow-hidden border border-slate-800">
        <div className="absolute top-0 right-0 p-10 text-right">
          <p className="text-blue-400 font-black text-[10px] uppercase tracking-[0.2em] mb-1">Probability Score</p>
          <h2 className="text-8xl font-black text-white leading-none">
            {data.selection_probability || 0}<span className="text-3xl text-slate-500">%</span>
          </h2>
        </div>

        <div className="max-w-2xl">
          <span className="px-4 py-1.5 bg-blue-500/10 text-blue-400 rounded-full text-[10px] font-black uppercase tracking-widest border border-blue-500/20 mb-6 inline-block">
            Internal Selection Dossier
          </span>
          <h1 className="text-5xl font-black mb-3 tracking-tight">{data.name}</h1>
          <p className="text-xl font-bold text-slate-400 mb-8">Targeting: <span className="text-blue-400">{data.job_title}</span></p>
          
          <div className="p-6 bg-white/5 rounded-3xl border border-white/10 backdrop-blur-md">
            <p className="text-lg font-medium leading-relaxed italic text-slate-200">
              "{data.prestige_insight || "Analyzing candidate trajectory..."}"
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* LEFT COLUMN: PEDIGREE & WEAKNESSES */}
        <div className="lg:col-span-5 space-y-8">
          <div className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm">
            <h3 className="font-black text-xs uppercase text-slate-500 mb-6 tracking-widest">Structural Audit</h3>
            <div className="space-y-4">
              {[
                { label: "Institutional Tier", value: "Tier 2/3 (BVP BVCOE)", status: "neutral" },
                { label: "Experience Quality", value: "Tier 1 (Deloitte, PwC, DRDL)", status: "verified" },
                { label: "Academic Standing", value: "High (8.5 CGPA)", status: "verified" },
                { label: "Research Impact", value: "International Prestige", status: "verified" }
              ].map((item, i) => (
                <div key={i} className="flex items-center justify-between p-4 bg-slate-50 rounded-2xl border border-slate-100">
                  <p className="text-xs font-bold text-slate-500">{item.label}</p>
                  <p className="text-xs font-black text-slate-800">{item.value}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-rose-50/50 p-8 rounded-[2.5rem] border border-rose-100">
            <h3 className="font-black text-xs uppercase text-rose-600 mb-6 tracking-widest">Resume Weaknesses</h3>
            <ul className="space-y-4">
              {data.evidence_audit?.weaknesses?.map((w: string, i: number) => (
                <li key={i} className="flex gap-3 text-sm font-bold text-slate-600 leading-snug">
                  <span className="text-rose-500">⚠</span> {w}
                </li>
              )) || (
                <li className="text-sm font-bold text-slate-400 italic">No structural gaps identified.</li>
              )}
            </ul>
          </div>
        </div>

        {/* RIGHT COLUMN: SKILLS & SUGGESTIONS */}
        <div className="lg:col-span-7 space-y-8">
          <div className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm">
            <h3 className="font-black text-xs uppercase text-slate-500 mb-6 tracking-widest">Skill Alignment Analysis</h3>
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-3">
                <p className="text-[10px] font-black text-emerald-600 uppercase tracking-widest">Matched</p>
                <div className="flex flex-wrap gap-2">
                  {data.matched_skills?.map((s: string, i: number) => (
                    <span key={i} className="text-[10px] font-bold px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-lg border border-emerald-100">{s}</span>
                  ))}
                </div>
              </div>
              <div className="space-y-3">
                <p className="text-[10px] font-black text-rose-500 uppercase tracking-widest">Missing</p>
                <div className="flex flex-wrap gap-2">
                  {data.missing_skills?.map((s: string, i: number) => (
                    <span key={i} className="text-[10px] font-bold px-3 py-1.5 bg-rose-50 text-rose-700 rounded-lg border border-rose-100">{s}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* ACTIONABLE IMPROVEMENTS */}
          <div className="bg-blue-600 p-8 rounded-[2.5rem] text-white shadow-xl shadow-blue-100">
            <h3 className="font-black text-xs uppercase text-blue-200 mb-6 tracking-widest">Refactoring Recommendations</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.evidence_audit?.suggestions?.map((s: any, i: number) => (
                <div key={i} className="bg-white/10 p-5 rounded-2xl border border-white/10">
                  <p className="text-[9px] font-black text-blue-200 uppercase mb-2">{s.type || "Suggestion"}</p>
                  <p className="text-sm font-bold leading-relaxed">{s.instruction}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-center pt-8">
        <button onClick={onBack} className="px-10 py-4 bg-slate-900 text-white rounded-full font-black text-sm hover:scale-105 transition-all shadow-xl">
          ← Back to Analysis
        </button>
      </div>
    </div>
  );
}