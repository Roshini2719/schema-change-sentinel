import React from 'react';
import { ShieldCheck, Layers, GitPullRequest, GitBranch, Activity, FileText, Settings } from 'lucide-react';

interface NavigationProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  backendStatus: boolean;
  onOpenAuth: () => void;
  isAuthenticated: boolean;
}

export const Header: React.FC<NavigationProps> = ({ activeTab, setActiveTab, backendStatus, onOpenAuth, isAuthenticated }) => {
  const tabs = [
    { id: 'dashboard', label: 'Executive Dashboard', icon: Activity },
    { id: 'schemas', label: 'Schemas & Contracts', icon: ShieldCheck },
    { id: 'runs', label: 'Pipeline Runs & Diffs', icon: GitPullRequest },
    { id: 'lineage', label: 'Downstream Lineage', icon: GitBranch },
    { id: 'audit', label: 'Audit Logs & Governance', icon: FileText },
  ];

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-slate-950/80 border-b border-slate-800/80 px-6 py-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-xl text-white tracking-tight">Schema Sentinel</h1>
              <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-mono">
                v1.0.0
              </span>
            </div>
            <p className="text-xs text-slate-400">Fintech Data Pipeline Guardrails & Contract Enforcer</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={onOpenAuth}
            className="px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-400 hover:text-white hover:border-slate-700 text-xs font-semibold transition"
          >
            Sign Out
          </button>
        </div>
      </div>

      <nav className="max-w-7xl mx-auto flex items-center gap-2 mt-4 overflow-x-auto pb-1">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition whitespace-nowrap ${
                isActive
                  ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
              {tab.label}
            </button>
          );
        })}
      </nav>
    </header>
  );
};
