import React, { useState } from 'react';
import { mockPipelineRuns } from '../services/api';
import { PipelineRun } from '../types';
import { CheckCircle2, AlertTriangle, XCircle, FileCode, ArrowRight } from 'lucide-react';

export const PipelineRunsTab: React.FC = () => {
  const [selectedRun, setSelectedRun] = useState<PipelineRun>(mockPipelineRuns[1]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Pipeline Evaluation Diffs & Runs</h2>
        <p className="text-sm text-slate-400">Deep-dive into breaking schema changes and execution logs</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Run list */}
        <div className="space-y-3">
          {mockPipelineRuns.map((run) => {
            const isSelected = selectedRun.id === run.id;
            return (
              <div
                key={run.id}
                onClick={() => setSelectedRun(run)}
                className={`p-4 rounded-xl cursor-pointer border transition ${
                  isSelected ? 'bg-slate-900 border-cyan-500/50 shadow-md' : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-xs text-cyan-400 font-semibold">{run.pipeline_id}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                    run.status === 'ALLOW' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                    run.status === 'WARN' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                    'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                  }`}>
                    {run.status}
                  </span>
                </div>
                <div className="text-sm font-medium text-white">{run.partner} Data Pipeline</div>
                <div className="text-xs text-slate-400 mt-1 flex items-center justify-between">
                  <span>{run.breaking_changes} breaking diff(s)</span>
                  <span>{run.timestamp}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Selected Run Visual Diff Inspector */}
        <div className="lg:col-span-2 space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
              <div>
                <span className="text-xs font-mono text-cyan-400">{selectedRun.pipeline_id}</span>
                <h3 className="text-lg font-bold text-white">{selectedRun.partner} Ingestion Execution Log</h3>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Decision:</span>
                <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold flex items-center gap-1.5 ${
                  selectedRun.status === 'ALLOW' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                  selectedRun.status === 'WARN' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                  'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                }`}>
                  {selectedRun.status === 'ALLOW' && <CheckCircle2 className="w-3.5 h-3.5" />}
                  {selectedRun.status === 'WARN' && <AlertTriangle className="w-3.5 h-3.5" />}
                  {selectedRun.status === 'BLOCK' && <XCircle className="w-3.5 h-3.5" />}
                  {selectedRun.status}
                </span>
              </div>
            </div>

            {/* Schema Diff Visualizer */}
            <div className="space-y-4">
              <h4 className="text-xs font-semibold uppercase text-slate-400 tracking-wider flex items-center gap-2">
                <FileCode className="w-4 h-4 text-cyan-400" /> Schema Diff Analysis (Contract vs Payload)
              </h4>

              <div className="p-4 rounded-xl bg-slate-950 font-mono text-xs text-slate-300 space-y-2 border border-slate-800">
                <div className="text-slate-500">// Schema structural diff comparison engine</div>
                <div className="text-slate-400">--- registered_contract_v2.4.json</div>
                <div className="text-slate-400">+++ incoming_partner_payload_902.json</div>
                
                <div className="mt-3 space-y-1">
                  <div className="text-slate-300">  "transaction_id": "string",</div>
                  <div className="bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded border border-rose-500/30">
                    - "amount": "DECIMAL(18,4)" [Required]
                  </div>
                  <div className="bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/30">
                    + "amount": "string" [Type Mismatch Violation]
                  </div>
                  <div className="bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded border border-rose-500/30">
                    - "category_id": "integer" [Field Dropped by Partner API]
                  </div>
                  <div className="text-slate-300">  "timestamp": "iso8601_date"</div>
                </div>
              </div>

              {selectedRun.details && (
                <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs">
                  <span className="font-semibold block mb-1">Sentinel Rule Engine Output:</span>
                  {selectedRun.details}
                </div>
              )}

              <div className="pt-4 flex justify-end gap-3">
                <button className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-medium text-xs transition">
                  Export Diff Report (JSON)
                </button>
                {selectedRun.status === 'BLOCK' && (
                  <button className="px-4 py-2 rounded-xl bg-rose-500 hover:bg-rose-400 text-slate-950 font-semibold text-xs transition flex items-center gap-1.5">
                    Override & Force Publish <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
