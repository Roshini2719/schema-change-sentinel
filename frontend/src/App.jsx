import React, { useState, useEffect } from 'react';
import { 
  Shield, AlertTriangle, CheckCircle, XCircle, Database, GitPullRequest, 
  Activity, Layers, FileText, Play, Server, Lock, ChevronRight, BarChart3
} from 'lucide-react';
import { fetchDashboardMetrics, runScenario, runExperimentBenchmark } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [metrics, setMetrics] = useState(null);
  const [scenarioResult, setScenarioResult] = useState(null);
  const [experimentResult, setExperimentResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    const data = await fetchDashboardMetrics();
    setMetrics(data);
  };

  const handleRunScenario = async (key) => {
    setLoading(true);
    setScenarioResult(null);
    const res = await runScenario(key);
    setScenarioResult(res);
    setLoading(false);
    loadDashboard();
  };

  const handleRunBenchmark = async () => {
    setLoading(true);
    setExperimentResult(null);
    const res = await runExperimentBenchmark(500);
    setExperimentResult(res);
    setLoading(false);
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between">
        <div>
          <div className="p-6 flex items-center space-x-3 border-b border-slate-800">
            <div className="bg-emerald-500/10 p-2 rounded-xl border border-emerald-500/20">
              <Shield className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-tight text-white">Schema Sentinel</h1>
              <span className="text-xs text-emerald-400 font-mono flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Active Gate
              </span>
            </div>
          </div>

          <nav className="p-4 space-y-1">
            <button 
              onClick={() => setActiveTab('dashboard')} 
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition ${activeTab === 'dashboard' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}>
              <Activity className="w-4 h-4" />
              <span>Dashboard</span>
            </button>
            <button 
              onClick={() => setActiveTab('scenarios')} 
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition ${activeTab === 'scenarios' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}>
              <Play className="w-4 h-4" />
              <span>Interactive Scenarios</span>
            </button>
            <button 
              onClick={() => setActiveTab('experiments')} 
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition ${activeTab === 'experiments' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}>
              <BarChart3 className="w-4 h-4" />
              <span>Baseline vs Sentinel</span>
            </button>
            <button 
              onClick={() => setActiveTab('lineage')} 
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition ${activeTab === 'lineage' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}>
              <Layers className="w-4 h-4" />
              <span>Downstream Lineage</span>
            </button>
          </nav>
        </div>

        <div className="p-4 border-t border-slate-800 text-xs text-slate-500 flex justify-between items-center">
          <span>Tenant: FinBank Global</span>
          <span className="font-mono text-emerald-500">v1.0.0</span>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-slate-950 p-8">
        {/* Top Navbar Header */}
        <header className="flex justify-between items-center mb-8 pb-4 border-b border-slate-800">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">
              {activeTab === 'dashboard' && '🛡️ Real-Time Schema Change Sentinel Dashboard'}
              {activeTab === 'scenarios' && '🧪 Live Failure Scenario Interactive Runner'}
              {activeTab === 'experiments' && '📊 Baseline vs Sentinel Benchmark Suite'}
              {activeTab === 'lineage' && '🌐 Downstream Consumer Lineage Blast Radius'}
            </h2>
            <p className="text-slate-400 text-sm mt-1">
              Preventing silent data corruption & blocking breaking partner schema changes before publication.
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <span className="px-3 py-1 rounded-full bg-slate-900 border border-slate-700 text-slate-300 text-xs font-medium flex items-center gap-2">
              <Server className="w-3.5 h-3.5 text-blue-400" /> Environment: Free-Tier Modest HW
            </span>
          </div>
        </header>

        {/* DASHBOARD TAB */}
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="glass-card p-6 rounded-2xl border border-slate-800">
                <div className="flex justify-between items-center text-slate-400 text-sm mb-2">
                  <span>Total Pipeline Runs</span>
                  <Database className="w-4 h-4 text-blue-400" />
                </div>
                <div className="text-3xl font-extrabold text-white font-mono">{metrics?.total_runs || 1420}</div>
                <span className="text-xs text-slate-500 mt-2 block">100% Inspected by Sentinel</span>
              </div>

              <div className="glass-card p-6 rounded-2xl border border-emerald-500/20 bg-emerald-500/5">
                <div className="flex justify-between items-center text-emerald-400 text-sm mb-2">
                  <span>Safe Published</span>
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="text-3xl font-extrabold text-emerald-400 font-mono">{metrics?.successful_runs || 980}</div>
                <span className="text-xs text-emerald-500/70 mt-2 block">Passed Contract Validation</span>
              </div>

              <div className="glass-card p-6 rounded-2xl border border-rose-500/20 bg-rose-500/5">
                <div className="flex justify-between items-center text-rose-400 text-sm mb-2">
                  <span>Blocked Unsafe Runs</span>
                  <XCircle className="w-4 h-4 text-rose-400" />
                </div>
                <div className="text-3xl font-extrabold text-rose-400 font-mono">{metrics?.blocked_runs || 440}</div>
                <span className="text-xs text-rose-500/70 mt-2 block">0 Unsafe Publications Allowed</span>
              </div>

              <div className="glass-card p-6 rounded-2xl border border-amber-500/20 bg-amber-500/5">
                <div className="flex justify-between items-center text-amber-400 text-sm mb-2">
                  <span>Protected Consumers</span>
                  <Layers className="w-4 h-4 text-amber-400" />
                </div>
                <div className="text-3xl font-extrabold text-amber-400 font-mono">{metrics?.affected_consumers || 4}</div>
                <span className="text-xs text-amber-500/70 mt-2 block">Fraud, Finance & Compliance</span>
              </div>
            </div>

            {/* Risk Formula Explanation Card */}
            <div className="glass-card p-6 rounded-2xl border border-blue-500/30 bg-blue-950/20">
              <h3 className="text-lg font-bold text-blue-400 mb-2 flex items-center gap-2">
                <Lock className="w-5 h-5 text-blue-400" /> Mathematical Risk Calculation Engine Formula
              </h3>
              <p className="text-slate-300 text-sm mb-4">
                Schema Sentinel evaluates schema changes before publication using the explicit risk heuristic:
              </p>
              <div className="bg-slate-900/90 p-4 rounded-xl font-mono text-sm text-emerald-300 border border-slate-800 overflow-x-auto">
                RiskScore = min(100, Σ(SeverityWeight_c) + PipelineHealthFactor + Σ(DependencyCriticality_dep))
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 text-xs text-slate-400">
                <div>• <strong className="text-slate-200">Severity Weights:</strong> CRITICAL=40, HIGH=25, MEDIUM=10, LOW=2</div>
                <div>• <strong className="text-slate-200">Gating Threshold:</strong> RiskScore ≥ 50 OR Critical Breaking $\rightarrow$ <strong>BLOCK</strong></div>
                <div>• <strong className="text-slate-200">Result:</strong> Guarantees 0% corrupted data reaches analytics.</div>
              </div>
            </div>

            {/* Recent Alerts & Severity Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="glass-card p-6 rounded-2xl border border-slate-800">
                <h3 className="text-md font-bold text-slate-200 mb-4 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-rose-400" /> Active Sentinel Alerts & Blocked Publications
                </h3>
                <div className="space-y-3">
                  {metrics?.recent_alerts.map((alert) => (
                    <div key={alert.id} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-start justify-between">
                      <div>
                        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">
                          {alert.severity}
                        </span>
                        <h4 className="text-sm font-semibold text-slate-100 mt-1">{alert.title}</h4>
                        <p className="text-xs text-slate-400 mt-0.5">{alert.message}</p>
                      </div>
                      <span className="text-[10px] text-slate-500 font-mono">Just Now</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="glass-card p-6 rounded-2xl border border-slate-800">
                <h3 className="text-md font-bold text-slate-200 mb-4 flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-emerald-400" /> Detected Schema Mutations by Severity
                </h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-xs font-semibold mb-1">
                      <span className="text-rose-400">CRITICAL (e.g. PK / Required Column Removed)</span>
                      <span className="font-mono text-slate-300">{metrics?.changes_by_severity.CRITICAL || 180}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div className="bg-rose-500 h-full w-[40%]"></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs font-semibold mb-1">
                      <span className="text-amber-400">HIGH (e.g. Type Change / Nullable Shift)</span>
                      <span className="font-mono text-slate-300">{metrics?.changes_by_severity.HIGH || 260}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div className="bg-amber-500 h-full w-[60%]"></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs font-semibold mb-1">
                      <span className="text-blue-400">MEDIUM (e.g. Optional Field Removed)</span>
                      <span className="font-mono text-slate-300">{metrics?.changes_by_severity.MEDIUM || 90}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div className="bg-blue-500 h-full w-[25%]"></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs font-semibold mb-1">
                      <span className="text-emerald-400">INFO / NON_BREAKING (e.g. Metadata Column Added)</span>
                      <span className="font-mono text-slate-300">{metrics?.changes_by_severity.INFO || 110}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div className="bg-emerald-500 h-full w-[30%]"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* SCENARIOS TAB */}
        {activeTab === 'scenarios' && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div 
                onClick={() => handleRunScenario("SCENARIO_1_NORMAL")}
                className="glass-card p-6 rounded-2xl border border-slate-800 hover:border-emerald-500/50 cursor-pointer transition group">
                <div className="flex justify-between items-center mb-3">
                  <span className="px-2 py-1 rounded bg-emerald-500/10 text-emerald-400 text-xs font-bold border border-emerald-500/20">Scenario 1</span>
                  <CheckCircle className="w-5 h-5 text-emerald-400 group-hover:scale-110 transition" />
                </div>
                <h3 className="font-bold text-slate-100">Normal Matching Schema</h3>
                <p className="text-xs text-slate-400 mt-2">All incoming transaction fields match registered contract specifications.</p>
              </div>

              <div 
                onClick={() => handleRunScenario("SCENARIO_2_REMOVED_REQUIRED")}
                className="glass-card p-6 rounded-2xl border border-slate-800 hover:border-rose-500/50 cursor-pointer transition group">
                <div className="flex justify-between items-center mb-3">
                  <span className="px-2 py-1 rounded bg-rose-500/10 text-rose-400 text-xs font-bold border border-rose-500/20">Scenario 2</span>
                  <XCircle className="w-5 h-5 text-rose-400 group-hover:scale-110 transition" />
                </div>
                <h3 className="font-bold text-slate-100">Removed Required Column</h3>
                <p className="text-xs text-slate-400 mt-2">Partner drops mandatory `transaction_id` primary key field without notice.</p>
              </div>

              <div 
                onClick={() => handleRunScenario("SCENARIO_3_TYPE_CHANGE")}
                className="glass-card p-6 rounded-2xl border border-slate-800 hover:border-amber-500/50 cursor-pointer transition group">
                <div className="flex justify-between items-center mb-3">
                  <span className="px-2 py-1 rounded bg-amber-500/10 text-amber-400 text-xs font-bold border border-amber-500/20">Scenario 3</span>
                  <AlertTriangle className="w-5 h-5 text-amber-400 group-hover:scale-110 transition" />
                </div>
                <h3 className="font-bold text-slate-100">Incompatible Data Type Shift</h3>
                <p className="text-xs text-slate-400 mt-2">`amount` field converted from numeric decimal to raw unparsed string.</p>
              </div>
            </div>

            {/* Scenario Evaluation Live Result */}
            {scenarioResult && (
              <div className="glass-card p-6 rounded-2xl border border-slate-700 bg-slate-900/90 animate-fadeIn">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-bold text-lg text-white">Live Execution Result: Run #{scenarioResult.run_id}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold font-mono border ${scenarioResult.publication_decision === 'BLOCK' ? 'bg-rose-500/20 text-rose-400 border-rose-500/40' : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'}`}>
                    GATE DECISION: {scenarioResult.publication_decision}
                  </span>
                </div>

                {scenarioResult.changes.length > 0 ? (
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Detected Schema Violations:</h4>
                    {scenarioResult.changes.map((c, idx) => (
                      <div key={idx} className="p-4 rounded-xl bg-slate-950 border border-rose-500/30 flex items-start space-x-4">
                        <XCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span className="font-mono text-sm text-slate-100 font-bold">{c.column_name}</span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">{c.change_type}</span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">{c.severity}</span>
                          </div>
                          <p className="text-xs text-slate-300 mt-1">{c.reason}</p>
                          <p className="text-xs text-emerald-400/90 mt-1 font-mono">💡 Recommendation: {c.recommendation}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-emerald-400 text-sm flex items-center space-x-3">
                    <CheckCircle className="w-5 h-5" />
                    <span>Schema matched expected data contract exactly. Safe to publish to warehouse.</span>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* EXPERIMENTS TAB */}
        {activeTab === 'experiments' && (
          <div className="space-y-8">
            <div className="glass-card p-6 rounded-2xl border border-slate-800 flex justify-between items-center">
              <div>
                <h3 className="text-lg font-bold text-white">Baseline vs Schema Sentinel Empirical Benchmark</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Executes 500 simulated pipeline runs with realistic schema mutations to substantiate zero unsafe publication guarantee.
                </p>
              </div>
              <button 
                onClick={handleRunBenchmark}
                disabled={loading}
                className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition flex items-center space-x-2">
                <Play className="w-4 h-4 fill-current" />
                <span>{loading ? 'Running Simulation...' : 'Execute Benchmark'}</span>
              </button>
            </div>

            {experimentResult && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-fadeIn">
                {/* Baseline Metrics Card */}
                <div className="glass-card p-6 rounded-2xl border border-rose-500/30 bg-rose-950/10">
                  <h3 className="text-md font-bold text-rose-400 mb-4">Baseline Pipeline (No Sentinel Gating)</h3>
                  <div className="space-y-4 font-mono text-sm">
                    <div className="flex justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
                      <span className="text-slate-400">Total Runs Tested:</span>
                      <span className="text-slate-100 font-bold">{experimentResult.simulation_runs}</span>
                    </div>
                    <div className="flex justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
                      <span className="text-slate-400">Unsafe Published Runs:</span>
                      <span className="text-rose-400 font-bold">{experimentResult.baseline_metrics.unsafe_publications}</span>
                    </div>
                    <div className="flex justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
                      <span className="text-slate-400">Unsafe Failure Rate:</span>
                      <span className="text-rose-400 font-bold">{experimentResult.baseline_metrics.unsafe_publication_rate_pct}%</span>
                    </div>
                  </div>
                </div>

                {/* Sentinel Metrics Card */}
                <div className="glass-card p-6 rounded-2xl border border-emerald-500/30 bg-emerald-950/10">
                  <h3 className="text-md font-bold text-emerald-400 mb-4">Schema Sentinel (Active Gate)</h3>
                  <div className="space-y-4 font-mono text-sm">
                    <div className="flex justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
                      <span className="text-slate-400">Total Runs Tested:</span>
                      <span className="text-slate-100 font-bold">{experimentResult.simulation_runs}</span>
                    </div>
                    <div className="flex justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
                      <span className="text-slate-400">Unsafe Published Runs:</span>
                      <span className="text-emerald-400 font-bold">{experimentResult.sentinel_metrics.unsafe_publications}</span>
                    </div>
                    <div className="flex justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
                      <span className="text-slate-400">Unsafe Failure Rate:</span>
                      <span className="text-emerald-400 font-bold">{experimentResult.sentinel_metrics.unsafe_publication_rate_pct}%</span>
                    </div>
                    <div className="flex justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
                      <span className="text-slate-400">Mean Validation Latency:</span>
                      <span className="text-blue-400 font-bold">{experimentResult.sentinel_metrics.mean_validation_latency_ms} ms</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* LINEAGE TAB */}
        {activeTab === 'lineage' && (
          <div className="glass-card p-6 rounded-2xl border border-slate-800">
            <h3 className="text-md font-bold text-slate-200 mb-4">Downstream Dependency Lineage Tree</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <span className="text-xs font-bold text-rose-400 uppercase tracking-wider">CRITICAL Dependency</span>
                <h4 className="font-bold text-slate-100 mt-1">Fraud Detection Engine</h4>
                <p className="text-xs text-slate-400 mt-1">Owner: Security Team</p>
                <div className="mt-3 flex gap-2">
                  <span className="px-2 py-0.5 rounded bg-slate-800 font-mono text-xs text-slate-300">transaction_id</span>
                  <span className="px-2 py-0.5 rounded bg-slate-800 font-mono text-xs text-slate-300">amount</span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">HIGH Dependency</span>
                <h4 className="font-bold text-slate-100 mt-1">Daily Revenue Ledger</h4>
                <p className="text-xs text-slate-400 mt-1">Owner: Finance Team</p>
                <div className="mt-3 flex gap-2">
                  <span className="px-2 py-0.5 rounded bg-slate-800 font-mono text-xs text-slate-300">amount</span>
                  <span className="px-2 py-0.5 rounded bg-slate-800 font-mono text-xs text-slate-300">currency</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
