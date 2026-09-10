import React from 'react';
import { mockAuditLogs } from '../services/api';
import { ShieldCheck, FileText, UserCheck, ShieldAlert } from 'lucide-react';

export const AuditTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Audit Logs & Governance History</h2>
        <p className="text-sm text-slate-400">Immutable trail of evaluation decisions, contract modifications, and manual overrides</p>
      </div>

      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" /> Security & Governance Trail
          </h3>
          <span className="text-xs font-mono text-slate-400">Showing last {mockAuditLogs.length} events</span>
        </div>

        <div className="space-y-3">
          {mockAuditLogs.map((log) => (
            <div key={log.id} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 mt-0.5">
                  {log.event.includes('OVERRIDE') ? (
                    <ShieldAlert className="w-4 h-4 text-amber-400" />
                  ) : (
                    <UserCheck className="w-4 h-4 text-cyan-400" />
                  )}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-white">{log.event}</span>
                    <span className="text-xs text-slate-400">by <strong className="text-slate-200">{log.user}</strong></span>
                  </div>
                  <p className="text-xs text-slate-300 mt-1">{log.reason}</p>
                  <div className="text-[10px] font-mono text-slate-500 mt-1">{log.timestamp}</div>
                </div>
              </div>

              <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold shrink-0 self-start md:self-center ${
                log.decision === 'BLOCK' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' :
                log.decision === 'ALLOW_OVERRIDE' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
              }`}>
                {log.decision}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
