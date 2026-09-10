import React from 'react';
import { mockDependencies } from '../services/api';
import { GitBranch, AlertTriangle, Layers, Table, Database } from 'lucide-react';

export const LineageTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Downstream Impact & SQL Lineage Analyzer</h2>
        <p className="text-sm text-slate-400">Automated propagation risk scoring across downstream dbt models, views, and dashboards</p>
      </div>

      {/* Visual Lineage Graph Representation */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-6">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <GitBranch className="w-4 h-4 text-cyan-400" /> Interactive Dependency Lineage Tree
        </h3>

        <div className="p-6 rounded-2xl bg-slate-950/80 border border-slate-800 overflow-x-auto">
          <div className="flex items-center justify-between min-w-[700px] gap-6">
            {/* Root Node */}
            <div className="p-4 rounded-xl bg-slate-900 border-2 border-rose-500 shadow-lg shadow-rose-500/20 text-center w-52">
              <div className="text-[10px] font-mono text-rose-400 uppercase font-bold mb-1">Upstream Upheaval</div>
              <div className="font-bold text-sm text-white flex items-center justify-center gap-1.5">
                <Database className="w-4 h-4 text-rose-400" /> stripe_payments
              </div>
              <div className="text-[11px] text-slate-400 mt-1">Field `amount` modified</div>
            </div>

            <div className="h-0.5 w-12 bg-gradient-to-r from-rose-500 to-amber-500 relative">
              <div className="absolute right-0 top-1/2 -translate-y-1/2 border-t-4 border-t-transparent border-b-4 border-b-transparent border-l-6 border-l-amber-500"></div>
            </div>

            {/* Downstream Stage 1 */}
            <div className="p-4 rounded-xl bg-slate-900 border border-amber-500/60 text-center w-56">
              <div className="text-[10px] font-mono text-amber-400 uppercase font-bold mb-1">Staging Layer</div>
              <div className="font-bold text-sm text-white flex items-center justify-center gap-1.5">
                <Table className="w-4 h-4 text-amber-400" /> stg_stripe_transactions
              </div>
              <div className="text-[11px] text-slate-400 mt-1">dbt Model (Depth 1)</div>
            </div>

            <div className="h-0.5 w-12 bg-gradient-to-r from-amber-500 to-cyan-500"></div>

            {/* Downstream Stage 2 */}
            <div className="space-y-3 w-60">
              <div className="p-3 rounded-xl bg-slate-900 border border-cyan-500/60 text-center">
                <div className="text-[10px] font-mono text-cyan-400 uppercase font-bold mb-0.5">Marts / Fact</div>
                <div className="font-bold text-xs text-white">fct_daily_reconciliation</div>
                <div className="text-[10px] text-slate-400">Risk: CRITICAL (Broke 4 aggregations)</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-700 text-center opacity-80">
                <div className="text-[10px] font-mono text-slate-400 uppercase font-bold mb-0.5">Marts / Dim</div>
                <div className="font-bold text-xs text-slate-300">dim_customer_accounts</div>
                <div className="text-[10px] text-slate-400">Risk: HIGH</div>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Impact Breakdown Table */}
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-slate-200">Impacted SQL Dependencies & Downstream Artifacts</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-xs tracking-wider">
                <tr>
                  <th className="py-3 px-4 rounded-l-lg">Model / Table Name</th>
                  <th className="py-3 px-4">Artifact Type</th>
                  <th className="py-3 px-4">Downstream Depth</th>
                  <th className="py-3 px-4">Impact Risk</th>
                  <th className="py-3 px-4 rounded-r-lg">Impacted Columns</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {mockDependencies.map((dep) => (
                  <tr key={dep.id} className="hover:bg-slate-850/50 transition">
                    <td className="py-3 px-4 font-mono font-medium text-white flex items-center gap-2">
                      <Layers className="w-4 h-4 text-cyan-400" />
                      {dep.model_name}
                    </td>
                    <td className="py-3 px-4 text-slate-400">{dep.table_type}</td>
                    <td className="py-3 px-4 font-mono text-xs text-slate-300">Level {dep.downstream_depth}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-mono font-bold ${
                        dep.risk_level === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' :
                        dep.risk_level === 'HIGH' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                        'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                      }`}>
                        {dep.risk_level}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-xs text-slate-400">
                      {dep.impacted_columns.join(', ')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
