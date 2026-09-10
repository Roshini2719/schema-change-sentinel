import React from 'react';
import { PipelineMetric, PipelineRun, DataSource } from '../types';
import { CheckCircle2, AlertTriangle, XCircle, ShieldAlert, Database, ArrowUpRight } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';

interface DashboardProps {
  metrics: PipelineMetric;
  pipelineRuns: PipelineRun[];
  dataSources: DataSource[];
  onNavigateToRuns: () => void;
}

const trendData = [
  { time: '00:00', allowed: 120, warned: 15, blocked: 2 },
  { time: '04:00', allowed: 180, warned: 22, blocked: 5 },
  { time: '08:00', allowed: 340, warned: 45, blocked: 12 },
  { time: '12:00', allowed: 290, warned: 38, blocked: 8 },
  { time: '16:00', allowed: 410, warned: 50, blocked: 18 },
  { time: '20:00', allowed: 230, warned: 20, blocked: 4 },
];

export const Dashboard: React.FC<DashboardProps> = ({ metrics, pipelineRuns, dataSources, onNavigateToRuns }) => {
  return (
    <div className="space-y-6">
      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Evaluations</span>
            <Database className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold text-white tracking-tight">{metrics.total_evaluations}</div>
          <div className="flex items-center gap-1.5 mt-2 text-xs text-emerald-400">
            <ArrowUpRight className="w-3.5 h-3.5" />
            <span>+14.2% from last week</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Allowed Pipelines</span>
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-400 tracking-tight">{metrics.total_allowed}</div>
          <div className="text-xs text-slate-400 mt-2">
            {((metrics.total_allowed / metrics.total_evaluations) * 100).toFixed(1)}% compliance rate
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Warned (Non-Breaking)</span>
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-amber-400 tracking-tight">{metrics.total_warned}</div>
          <div className="text-xs text-slate-400 mt-2">Minor schema drifts detected</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Blocked (Unsafe)</span>
            <XCircle className="w-5 h-5 text-rose-400" />
          </div>
          <div className="text-3xl font-extrabold text-rose-400 tracking-tight">{metrics.total_blocked}</div>
          <div className="text-xs text-rose-300/80 mt-2 flex items-center gap-1">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Prevented downstream failures</span>
          </div>
        </div>
      </div>

      {/* Chart & Active Sources */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-base font-semibold text-white">Pipeline Publication Activity</h3>
              <p className="text-xs text-slate-400">Decision breakdown across 24h evaluation cycles</p>
            </div>
            <div className="flex items-center gap-4 text-xs font-medium">
              <span className="flex items-center gap-1.5 text-emerald-400">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span> ALLOW
              </span>
              <span className="flex items-center gap-1.5 text-amber-400">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span> WARN
              </span>
              <span className="flex items-center gap-1.5 text-rose-400">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-400"></span> BLOCK
              </span>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="colorAllowed" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorBlocked" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#475569" fontSize={12} />
                <YAxis stroke="#475569" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem' }} 
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Area type="monotone" dataKey="allowed" stroke="#10b981" fillOpacity={1} fill="url(#colorAllowed)" />
                <Area type="monotone" dataKey="blocked" stroke="#f43f5e" fillOpacity={1} fill="url(#colorBlocked)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-semibold text-white mb-1">Active Data Sources</h3>
            <p className="text-xs text-slate-400 mb-4">Monitored ingestion endpoints & partners</p>
            <div className="space-y-3">
              {dataSources.map((source) => (
                <div key={source.id} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-slate-200">{source.name}</div>
                    <div className="text-xs text-slate-400">{source.partner_name} • {source.source_type}</div>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-mono font-semibold ${
                    source.status === 'ACTIVE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  }`}>
                    {source.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <button 
            onClick={onNavigateToRuns}
            className="w-full mt-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-medium text-sm transition shadow-md shadow-cyan-500/20"
          >
            Review Recent Runs & Breaking Diffs →
          </button>
        </div>
      </div>

      {/* Live Pipeline Feed */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-white">Recent Pipeline Governance Evaluations</h3>
          <span className="text-xs text-cyan-400 font-mono">Live updates</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/60 text-slate-400 uppercase text-xs tracking-wider">
              <tr>
                <th className="py-3 px-4 rounded-l-lg">Pipeline ID</th>
                <th className="py-3 px-4">Partner</th>
                <th className="py-3 px-4">Publication Decision</th>
                <th className="py-3 px-4">Breaking Changes</th>
                <th className="py-3 px-4">Execution Time</th>
                <th className="py-3 px-4 rounded-r-lg">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {pipelineRuns.map((run) => (
                <tr key={run.id} className="hover:bg-slate-850/50 transition">
                  <td className="py-3.5 px-4 font-mono text-cyan-400">{run.pipeline_id}</td>
                  <td className="py-3.5 px-4 font-medium text-slate-200">{run.partner}</td>
                  <td className="py-3.5 px-4">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold font-mono ${
                      run.status === 'ALLOW' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                      run.status === 'WARN' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                      'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                    }`}>
                      {run.status === 'ALLOW' && <CheckCircle2 className="w-3.5 h-3.5" />}
                      {run.status === 'WARN' && <AlertTriangle className="w-3.5 h-3.5" />}
                      {run.status === 'BLOCK' && <XCircle className="w-3.5 h-3.5" />}
                      {run.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-mono font-medium text-slate-300">{run.breaking_changes}</td>
                  <td className="py-3.5 px-4 text-slate-400">{run.execution_time_ms} ms</td>
                  <td className="py-3.5 px-4 text-slate-400 font-mono text-xs">{run.timestamp}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
