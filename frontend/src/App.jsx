import { useState, useEffect, useCallback } from 'react';
import './index.css';
import { api, setToken, clearToken, getToken } from './api.js';

// ─── Utilities ────────────────────────────────────────────────────────────────
const fmtDate = (s) => s ? new Date(s).toLocaleString() : '—';
const initials = (name) => name ? name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0,2) : '?';

function roleBadge(role) {
  const map = { ADMIN: 'badge-admin', DATA_ENGINEER: 'badge-engineer', ANALYST: 'badge-analyst', PARTNER: 'badge-partner' };
  const label = { ADMIN: 'Admin', DATA_ENGINEER: 'Engineer', ANALYST: 'Analyst', PARTNER: 'Partner' };
  return <span className={`badge ${map[role] || 'badge-info'}`}>{label[role] || role}</span>;
}

function decisionBadge(d) {
  if (!d) return null;
  const cls = d === 'ALLOW' ? 'badge-allow' : d === 'BLOCK' ? 'badge-block' : 'badge-warning';
  const icon = d === 'ALLOW' ? '✅' : d === 'BLOCK' ? '🚫' : '⚠️';
  return <span className={`badge ${cls}`}>{icon} {d}</span>;
}

// ─── Toast ────────────────────────────────────────────────────────────────────
function Toast({ toasts }) {
  return (
    <div className="toast-container">
      {toasts.map(t => (
        <div key={t.id} className={`toast toast-${t.type}`}>
          {t.type === 'success' ? '✅' : '❌'} {t.msg}
        </div>
      ))}
    </div>
  );
}

// ─── Login ────────────────────────────────────────────────────────────────────
const DEMO_CREDS = [
  { email: 'admin@finbank.com', password: 'admin123', label: 'Admin (FinBank)', role: 'ADMIN' },
  { email: 'engineer@finbank.com', password: 'engineer123', label: 'Data Engineer', role: 'DATA_ENGINEER' },
  { email: 'analyst@finbank.com', password: 'analyst123', label: 'Analyst', role: 'ANALYST' },
  { email: 'partner@partnera.com', password: 'partner123', label: 'Partner (PartnerA)', role: 'PARTNER' },
  { email: 'admin@clearpay.com', password: 'admin123', label: 'Admin (ClearPay)', role: 'ADMIN' },
];

function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e) => {
    e?.preventDefault();
    setLoading(true); setError('');
    try {
      const res = await api.login(email, password);
      setToken(res.access_token);
      localStorage.setItem('scs_user', JSON.stringify(res.user));
      onLogin(res.user);
    } catch (err) { setError(err.message || 'Login failed'); }
    finally { setLoading(false); }
  };

  const quickLogin = (c) => { setEmail(c.email); setPassword(c.password); };

  return (
    <div className="login-page">
      <div className="login-box">
        <div className="login-logo">
          <span className="logo-icon">🛡️</span>
          <h1>Schema Change Sentinel</h1>
          <p>Fintech data pipeline protection</p>
        </div>
        <form onSubmit={submit}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="user@org.com" required />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required />
          </div>
          {error && <div style={{ color: 'var(--danger)', fontSize: 12, marginBottom: 12 }}>⚠️ {error}</div>}
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? <><span className="spinner" /> Signing in...</> : '🔑 Sign In'}
          </button>
        </form>
        <div className="demo-creds">
          <h4>Demo Credentials</h4>
          {DEMO_CREDS.map(c => (
            <button key={c.email} className="demo-cred-btn" onClick={() => quickLogin(c)}>
              <span>{roleBadge(c.role)}</span>
              <span>{c.label}</span>
              <span style={{ marginLeft: 'auto', color: 'var(--text-muted)' }}>{c.email}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Sidebar ──────────────────────────────────────────────────────────────────
const NAV = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'scenarios', label: 'Demo Scenarios', icon: '🎬' },
  { id: 'schemas',   label: 'Schema Registry', icon: '📋' },
  { id: 'runs',      label: 'Pipeline Runs', icon: '⚡' },
  { id: 'audit',     label: 'Audit Logs', icon: '📝' },
  { id: 'validate',  label: 'Validate Schema', icon: '🔍' },
  { id: 'experiment',label: 'Experiment Results', icon: '🧪' },
];

function Sidebar({ page, setPage, user, onLogout }) {
  const adminNav = [{ id: 'admin', label: 'Admin Panel', icon: '⚙️' }];
  const allNav = user?.role === 'ADMIN' ? [...NAV, ...adminNav] : NAV;

  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <h2>🛡️ Schema Sentinel</h2>
        <p>Pipeline Protection</p>
      </div>
      <nav className="sidebar-nav">
        <div className="nav-section-label">Navigation</div>
        {allNav.map(n => (
          <button key={n.id} className={`nav-item ${page === n.id ? 'active' : ''}`} onClick={() => setPage(n.id)}>
            <span className="nav-icon">{n.icon}</span>
            {n.label}
          </button>
        ))}
      </nav>
      <div className="sidebar-user">
        <div className="user-avatar">{initials(user?.full_name || user?.email)}</div>
        <div className="user-info">
          <div className="user-name">{user?.full_name || user?.email}</div>
          <div className="user-role-label">{user?.role}</div>
        </div>
        <button className="btn btn-ghost" style={{ padding: '4px 8px', fontSize: 11 }} onClick={onLogout}>↩</button>
      </div>
    </div>
  );
}

// ─── Dashboard ────────────────────────────────────────────────────────────────
function Dashboard({ user }) {
  const [runs, setRuns] = useState([]);
  const [schemas, setSchemas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getPipelineRuns(), api.getSchemas()])
      .then(([r, s]) => { setRuns(r); setSchemas(s); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const blocked = runs.filter(r => r.gate_decision === 'BLOCK').length;
  const allowed = runs.filter(r => r.gate_decision === 'ALLOW').length;
  const totalBreaking = runs.reduce((s, r) => s + r.breaking_changes_count, 0);
  const safeRate = runs.length ? Math.round((allowed / runs.length) * 100) : 100;

  return (
    <div>
      <div className="page-header">
        <h1>📊 Dashboard</h1>
        <p>Real-time pipeline health for {user?.organisation_id?.slice(0,8)}...</p>
      </div>
      <div className="page-content">
        {loading ? <div style={{textAlign:'center',padding:40}}><span className="spinner" /></div> : (
          <>
            <div className="grid-4 section-gap">
              <StatCard label="Pipeline Runs" value={runs.length} sub="All time" color="var(--accent-blue)" />
              <StatCard label="Blocked (BLOCK)" value={blocked} sub="Breaking changes detected" color="var(--danger)" />
              <StatCard label="Published (ALLOW)" value={allowed} sub="Safe publications" color="var(--success)" />
              <StatCard label="Safe Rate" value={`${safeRate}%`} sub="Of all runs published" color="var(--accent-purple)" />
            </div>
            <div className="grid-2 section-gap">
              <div className="card">
                <div className="card-title">🚨 Recent Blocked Runs</div>
                {runs.filter(r => r.gate_decision === 'BLOCK').slice(0,5).map(r => (
                  <div key={r.id} style={{ display:'flex', justifyContent:'space-between', padding:'8px 0', borderBottom:'1px solid var(--border)', fontSize:12 }}>
                    <span className="mono">{r.id.slice(0,12)}...</span>
                    <span style={{ color:'var(--danger)' }}>🚫 {r.breaking_changes_count} breaking</span>
                    <span style={{ color:'var(--text-muted)' }}>{fmtDate(r.run_timestamp)}</span>
                  </div>
                ))}
                {runs.filter(r => r.gate_decision === 'BLOCK').length === 0 && <div className="empty-state"><p>No blocked runs</p></div>}
              </div>
              <div className="card">
                <div className="card-title">📋 Registered Schemas</div>
                {schemas.map(s => (
                  <div key={s.id} style={{ display:'flex', justifyContent:'space-between', padding:'8px 0', borderBottom:'1px solid var(--border)', fontSize:12 }}>
                    <span style={{ color:'var(--text-primary)', fontWeight:500 }}>{s.name}</span>
                    <span className="badge badge-info">v{s.version}</span>
                    <span style={{ color:'var(--text-muted)' }}>{s.columns?.length || 0} cols</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="card section-gap">
              <div className="card-title" style={{marginBottom:12}}>📈 Experiment Summary — Baseline vs Sentinel</div>
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:24 }}>
                <div>
                  <div style={{ fontSize:12, color:'var(--text-muted)', marginBottom:6 }}>Baseline (naive column-diff)</div>
                  <div style={{ fontSize:28, fontWeight:800, color:'var(--danger)' }}>~71%</div>
                  <div style={{ fontSize:12, color:'var(--text-muted)' }}>Unsafe publication rate</div>
                  <div className="metric-bar" style={{marginTop:8}}>
                    <div className="metric-bar-fill" style={{ width:'71%', background:'var(--danger)' }} />
                  </div>
                </div>
                <div>
                  <div style={{ fontSize:12, color:'var(--text-muted)', marginBottom:6 }}>Sentinel (this system)</div>
                  <div style={{ fontSize:28, fontWeight:800, color:'var(--success)' }}>0%</div>
                  <div style={{ fontSize:12, color:'var(--text-muted)' }}>Unsafe publication rate</div>
                  <div className="metric-bar" style={{marginTop:8}}>
                    <div className="metric-bar-fill" style={{ width:'2%', background:'var(--success)' }} />
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, sub, color }) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={{ color }}>{value}</div>
      <div className="stat-sub">{sub}</div>
    </div>
  );
}

// ─── Demo Scenarios ───────────────────────────────────────────────────────────
function ScenariosPage() {
  const [scenarios, setScenarios] = useState([]);
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState({});

  useEffect(() => {
    api.getScenarios().then(setScenarios).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const runAll = async () => {
    for (const s of scenarios) await runOne(s.id);
  };

  const runOne = async (id) => {
    setRunning(r => ({ ...r, [id]: true }));
    try {
      const res = await api.runScenario(id);
      setResults(r => ({ ...r, [id]: res }));
    } catch (err) {
      setResults(r => ({ ...r, [id]: { error: err.message } }));
    }
    setRunning(r => ({ ...r, [id]: false }));
  };

  if (loading) return <div style={{ padding: 40, textAlign: 'center' }}><span className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <h1>🎬 Demo Scenarios</h1>
        <p>Interactive validation scenarios demonstrating sentinel behaviour</p>
      </div>
      <div className="page-content">
        <div className="section-header">
          <h2 className="section-title">7 Pre-Built Scenarios</h2>
          <button className="btn btn-primary" onClick={runAll}>▶ Run All Scenarios</button>
        </div>
        <div className="scenario-grid">
          {scenarios.map(s => {
            const res = results[s.id];
            const isRunning = running[s.id];
            const cls = isRunning ? 'loading' : res ? (res.actual_decision === 'ALLOW' ? 'result-allow' : 'result-block') : '';
            return (
              <div key={s.id} className={`scenario-card ${cls}`}>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:6 }}>
                  <div className="scenario-name">{s.name}</div>
                  <span className="badge badge-info" style={{ flexShrink:0, marginLeft:8 }}>{s.id.toUpperCase()}</span>
                </div>
                <div className="scenario-desc">{s.description}</div>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12 }}>
                  <span style={{ fontSize:11, color:'var(--text-muted)' }}>Expected: {decisionBadge(s.expected_decision)}</span>
                  {res && !res.error && <span style={{ fontSize:11 }}>Actual: {decisionBadge(res.actual_decision)}</span>}
                </div>
                {res && !res.error && (
                  <div style={{ marginBottom:10 }}>
                    <div style={{ fontSize:11, color:'var(--text-muted)', marginBottom:6 }}>
                      {res.breaking_changes_count} breaking · {res.warning_changes_count} warning · {res.latency_ms}ms
                      {res.is_fail_closed && <span style={{ color:'var(--warning)', marginLeft:6 }}>⚡ fail-closed</span>}
                    </div>
                    {res.breaking_changes?.map((c, i) => (
                      <div key={i} className="change-item breaking">
                        <div className="change-header">
                          <span className="badge badge-block">{c.change_type}</span>
                          <span className="mono">{c.column_name}</span>
                          {c.old_value && c.new_value && <span style={{ color:'var(--text-muted)' }}>{c.old_value} → {c.new_value}</span>}
                        </div>
                        <div className="change-reason">{c.reason}</div>
                        <div className="change-rec">💡 {c.recommendation}</div>
                        {c.affected_consumers?.length > 0 && (
                          <div style={{ marginTop:4 }}>
                            {c.affected_consumers.map(cn => <span key={cn} className="consumer-tag">🔗 {cn}</span>)}
                          </div>
                        )}
                      </div>
                    ))}
                    {res.warning_changes?.map((c, i) => (
                      <div key={i} className="change-item warning">
                        <div className="change-header">
                          <span className="badge badge-warning">{c.change_type}</span>
                          <span className="mono">{c.column_name}</span>
                        </div>
                        <div className="change-reason">{c.reason}</div>
                      </div>
                    ))}
                    <div style={{ marginTop:8 }}>
                      {res.correct ? (
                        <span style={{ color:'var(--success)', fontSize:12, fontWeight:600 }}>✅ Sentinel decision correct</span>
                      ) : (
                        <span style={{ color:'var(--danger)', fontSize:12, fontWeight:600 }}>❌ Unexpected decision</span>
                      )}
                    </div>
                  </div>
                )}
                {res?.error && <div style={{ color:'var(--danger)', fontSize:12 }}>Error: {res.error}</div>}
                <button className="btn btn-secondary" style={{ width:'100%', marginTop:4 }} onClick={() => runOne(s.id)} disabled={isRunning}>
                  {isRunning ? <><span className="spinner" /> Running...</> : '▶ Run Scenario'}
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ─── Schema Registry ──────────────────────────────────────────────────────────
function SchemasPage() {
  const [schemas, setSchemas] = useState([]);
  const [selected, setSelected] = useState(null);
  const [deps, setDeps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSchemas().then(setSchemas).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const selectSchema = async (s) => {
    setSelected(s);
    try {
      const d = await api.getDependencies(s.id);
      setDeps(d);
    } catch { setDeps([]); }
  };

  return (
    <div>
      <div className="page-header">
        <h1>📋 Schema Registry</h1>
        <p>Registered data schemas and downstream dependencies</p>
      </div>
      <div className="page-content">
        {loading ? <div style={{ textAlign: 'center', padding: 40 }}><span className="spinner" /></div> : (
          <div className="grid-2">
            <div>
              <h2 className="section-title" style={{ marginBottom:12 }}>Schemas</h2>
              {schemas.map(s => (
                <div key={s.id} className={`card`} style={{ cursor:'pointer', marginBottom:10, borderColor: selected?.id === s.id ? 'var(--accent-blue)' : '' }}
                  onClick={() => selectSchema(s)}>
                  <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                    <div style={{ fontWeight:600, color:'var(--text-primary)' }}>{s.name}</div>
                    <span className="badge badge-info">v{s.version}</span>
                  </div>
                  <div style={{ fontSize:11, color:'var(--text-muted)', marginTop:4 }}>
                    {s.columns?.length || 0} columns · Created {fmtDate(s.created_at).split(',')[0]}
                  </div>
                </div>
              ))}
            </div>
            {selected && (
              <div>
                <h2 className="section-title" style={{ marginBottom:12 }}>{selected.name}</h2>
                <div className="card" style={{ marginBottom:12 }}>
                  <div className="card-title">Columns ({selected.columns?.length})</div>
                  {selected.columns?.map(c => (
                    <div key={c.id} className="col-row">
                      {c.is_primary_key && <span title="Primary Key" style={{ color:'var(--warning)' }}>🔑</span>}
                      {!c.is_primary_key && c.is_required && <span title="Required" style={{ color:'var(--danger)' }}>*</span>}
                      {!c.is_required && <span title="Optional" style={{ color:'var(--text-muted)' }}>○</span>}
                      <span className="col-name">{c.column_name}</span>
                      <span className="col-type">{c.data_type}</span>
                      {c.is_nullable && <span className="badge badge-warning" style={{ padding:'1px 6px' }}>nullable</span>}
                    </div>
                  ))}
                </div>
                <div className="card">
                  <div className="card-title">Downstream Dependencies ({deps.length})</div>
                  {deps.length === 0 && <div className="empty-state"><p>No dependencies registered</p></div>}
                  {deps.map(d => (
                    <div key={d.id} style={{ padding:'8px 0', borderBottom:'1px solid var(--border)', fontSize:12 }}>
                      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                        <span style={{ fontWeight:600, color:'var(--text-primary)' }}>{d.consumer_name}</span>
                        <span className={`badge ${d.criticality === 'CRITICAL' ? 'badge-block' : 'badge-warning'}`}>{d.criticality}</span>
                      </div>
                      <div style={{ color:'var(--text-muted)', marginTop:2 }}>{d.consumer_type}</div>
                      <div style={{ marginTop:4 }}>
                        {(d.columns_used || []).map(c => <span key={c} className="mono" style={{ background:'var(--bg-secondary)', padding:'1px 6px', borderRadius:4, marginRight:4, fontSize:11 }}>{c}</span>)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Pipeline Runs ─────────────────────────────────────────────────────────────
function RunsPage() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    api.getPipelineRuns().then(setRuns).catch(() => {}).finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>⚡ Pipeline Runs</h1>
        <p>History of all validation gate decisions</p>
      </div>
      <div className="page-content">
        {loading ? <div style={{ textAlign:'center', padding:40 }}><span className="spinner" /></div> : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Run ID</th>
                  <th>Timestamp</th>
                  <th>Gate Decision</th>
                  <th>Breaking</th>
                  <th>Warnings</th>
                  <th>Triggered By</th>
                </tr>
              </thead>
              <tbody>
                {runs.map(r => (
                  <tr key={r.id} style={{ cursor:'pointer' }} onClick={() => setSelected(selected?.id === r.id ? null : r)}>
                    <td className="mono">{r.id.slice(0,16)}...</td>
                    <td>{fmtDate(r.run_timestamp)}</td>
                    <td>{decisionBadge(r.gate_decision)}</td>
                    <td style={{ color: r.breaking_changes_count > 0 ? 'var(--danger)' : 'var(--text-muted)' }}>
                      {r.breaking_changes_count}
                    </td>
                    <td style={{ color: r.warning_changes_count > 0 ? 'var(--warning)' : 'var(--text-muted)' }}>
                      {r.warning_changes_count}
                    </td>
                    <td className="mono">{r.triggered_by || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {runs.length === 0 && <div className="empty-state"><div className="empty-icon">⚡</div><p>No pipeline runs yet. Run a demo scenario to start.</p></div>}
          </div>
        )}
        {selected && (
          <div className="card" style={{ marginTop:16 }}>
            <div className="card-title">Run Detail — {selected.id}</div>
            {selected.error_message && <div style={{ color:'var(--warning)', fontSize:12, marginBottom:8 }}>⚡ Fail-closed: {selected.error_message}</div>}
            <div style={{ fontSize:12, color:'var(--text-secondary)', marginBottom:8 }}>Changes detected:</div>
            {(selected.changes_detected || []).map((c, i) => (
              <div key={i} className={`change-item ${c.category === 'BREAKING' ? 'breaking' : c.category === 'WARNING' ? 'warning' : 'info'}`} style={{ marginBottom:6 }}>
                <div className="change-header">
                  <span className={`badge ${c.category === 'BREAKING' ? 'badge-block' : 'badge-warning'}`}>{c.change_type}</span>
                  <span className="mono">{c.column_name}</span>
                  {c.old_value && <span style={{ color:'var(--text-muted)' }}>{c.old_value} → {c.new_value || 'removed'}</span>}
                </div>
                <div className="change-reason">{c.reason}</div>
              </div>
            ))}
            {(!selected.changes_detected || selected.changes_detected.length === 0) && (
              <div style={{ color:'var(--success)', fontSize:12 }}>✅ No changes detected — clean publication</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Audit Logs ────────────────────────────────────────────────────────────────
function AuditPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  const load = useCallback(() => {
    setLoading(true);
    api.getAuditLogs(filter).then(setLogs).catch(() => {}).finally(() => setLoading(false));
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  return (
    <div>
      <div className="page-header">
        <h1>📝 Audit Logs</h1>
        <p>Complete trail of all gate decisions and user actions</p>
      </div>
      <div className="page-content">
        <div style={{ display:'flex', gap:10, marginBottom:16 }}>
          <input value={filter} onChange={e => setFilter(e.target.value)} placeholder="Filter by action (e.g. GATE_BLOCK)" style={{ maxWidth:300 }} />
          <button className="btn btn-secondary" onClick={load}>🔄 Refresh</button>
        </div>
        {loading ? <div style={{ textAlign:'center', padding:40 }}><span className="spinner" /></div> : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Action</th>
                  <th>User</th>
                  <th>Resource</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.map(l => (
                  <tr key={l.id}>
                    <td className="mono" style={{ fontSize:11 }}>{fmtDate(l.timestamp)}</td>
                    <td>
                      <span className={`badge ${l.action.includes('BLOCK') ? 'badge-block' : l.action.includes('ALLOW') ? 'badge-allow' : 'badge-info'}`}>
                        {l.action}
                      </span>
                    </td>
                    <td style={{ fontSize:12 }}>{l.user_email || '—'}</td>
                    <td className="mono" style={{ fontSize:11 }}>{l.resource_type || '—'}</td>
                    <td style={{ fontSize:11, color:'var(--text-muted)' }}>
                      {l.details ? `${l.details.breaking_changes ?? 0} breaking, ${l.details.latency_ms ?? '?'}ms` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {logs.length === 0 && <div className="empty-state"><div className="empty-icon">📝</div><p>No audit logs yet.</p></div>}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Validate Schema (manual) ──────────────────────────────────────────────────
const COLUMN_TYPES = ['string','integer','decimal','boolean','datetime','date'];

function ValidatePage() {
  const [schemas, setSchemas] = useState([]);
  const [schemaId, setSchemaId] = useState('');
  const [cols, setCols] = useState([{ column_name:'', data_type:'string', is_nullable:false }]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => { api.getSchemas().then(s => { setSchemas(s); if (s.length) setSchemaId(s[0].id); }); }, []);

  const addCol = () => setCols([...cols, { column_name:'', data_type:'string', is_nullable:false }]);
  const rmCol = (i) => setCols(cols.filter((_,j) => j !== i));
  const updCol = (i, k, v) => setCols(cols.map((c,j) => j === i ? {...c, [k]: v} : c));

  const submit = async () => {
    if (!schemaId) return;
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await api.validate({ schema_id: schemaId, incoming_columns: cols, run_label: 'manual-validate' });
      setResult(res);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div>
      <div className="page-header">
        <h1>🔍 Validate Schema</h1>
        <p>Manually submit an incoming schema for gate validation</p>
      </div>
      <div className="page-content">
        <div className="grid-2">
          <div>
            <div className="card section-gap">
              <div className="card-title">Validation Request</div>
              <div className="form-group">
                <label>Registered Schema</label>
                <select value={schemaId} onChange={e => setSchemaId(e.target.value)}>
                  {schemas.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Incoming Columns</label>
                {cols.map((c, i) => (
                  <div key={i} style={{ display:'flex', gap:8, marginBottom:6, alignItems:'center' }}>
                    <input value={c.column_name} onChange={e => updCol(i,'column_name',e.target.value)} placeholder="column_name" style={{ flex:2 }} />
                    <select value={c.data_type} onChange={e => updCol(i,'data_type',e.target.value)} style={{ flex:1 }}>
                      {COLUMN_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                    <label style={{ display:'flex', alignItems:'center', gap:4, margin:0, fontSize:11, whiteSpace:'nowrap', color:'var(--text-muted)' }}>
                      <input type="checkbox" checked={c.is_nullable} onChange={e => updCol(i,'is_nullable',e.target.checked)} />
                      nullable
                    </label>
                    <button className="btn btn-ghost" style={{ padding:'4px 8px' }} onClick={() => rmCol(i)}>✕</button>
                  </div>
                ))}
                <button className="btn btn-ghost" style={{ marginTop:4 }} onClick={addCol}>+ Add Column</button>
              </div>
              {error && <div style={{ color:'var(--danger)', fontSize:12, marginBottom:8 }}>⚠️ {error}</div>}
              <button className="btn btn-primary" onClick={submit} disabled={loading || !schemaId}>
                {loading ? <><span className="spinner" /> Validating...</> : '🔍 Run Validation'}
              </button>
            </div>
          </div>
          <div>
            {result && (
              <div>
                <div className={`gate-banner ${result.decision.toLowerCase()}`}>
                  {result.decision === 'ALLOW' ? '✅' : '🚫'} Gate Decision: {result.decision}
                  {result.is_fail_closed && <span style={{ fontSize:12, marginLeft:8 }}>⚡ Fail-closed</span>}
                </div>
                <div style={{ fontSize:12, color:'var(--text-muted)', marginBottom:12 }}>{result.reason}</div>
                <div className="changes-list">
                  {result.breaking_changes?.map((c,i) => (
                    <div key={i} className="change-item breaking">
                      <div className="change-header">
                        <span className="badge badge-block">{c.change_type}</span>
                        <span className="mono">{c.column_name}</span>
                        {c.old_value && <span style={{ color:'var(--text-muted)' }}>{c.old_value}→{c.new_value||'removed'}</span>}
                      </div>
                      <div className="change-reason">{c.reason}</div>
                      <div className="change-rec">💡 {c.recommendation}</div>
                    </div>
                  ))}
                  {result.warning_changes?.map((c,i) => (
                    <div key={i} className="change-item warning">
                      <div className="change-header">
                        <span className="badge badge-warning">{c.change_type}</span>
                        <span className="mono">{c.column_name}</span>
                      </div>
                      <div className="change-reason">{c.reason}</div>
                    </div>
                  ))}
                  {result.info_changes?.map((c,i) => (
                    <div key={i} className="change-item info">
                      <div className="change-header">
                        <span className="badge badge-info">{c.change_type}</span>
                        <span className="mono">{c.column_name}</span>
                      </div>
                      <div className="change-reason">{c.reason}</div>
                    </div>
                  ))}
                  {result.breaking_changes?.length === 0 && result.warning_changes?.length === 0 && (
                    <div style={{ color:'var(--success)', fontSize:13 }}>✅ No issues detected — safe to publish</div>
                  )}
                </div>
                {result.affected_consumers?.length > 0 && (
                  <div style={{ marginTop:12 }}>
                    <div style={{ fontSize:12, color:'var(--text-muted)', marginBottom:6 }}>Affected consumers:</div>
                    {result.affected_consumers.map(c => <span key={c} className="consumer-tag">🔗 {c}</span>)}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Experiment Results ────────────────────────────────────────────────────────
const EXP_DATA = {
  baseline_accuracy_pct: 40,
  sentinel_accuracy_pct: 100,
  baseline_unsafe_pub_rate_pct: 71,
  sentinel_unsafe_pub_rate_pct: 0,
  improvement_percentage_points: 71,
  scenarios: [
    { scenario_id:'S1', scenario_name:'Normal Data — All Fields Present',            expected:'ALLOW', baseline:'ALLOW', sentinel:'ALLOW', baseline_correct:true,  sentinel_correct:true },
    { scenario_id:'S2', scenario_name:'Required Column Removed (transaction_id)',    expected:'BLOCK', baseline:'BLOCK', sentinel:'BLOCK', baseline_correct:true,  sentinel_correct:true },
    { scenario_id:'S3', scenario_name:'Type Change — amount: decimal → string',      expected:'BLOCK', baseline:'ALLOW', sentinel:'BLOCK', baseline_correct:false, sentinel_correct:true },
    { scenario_id:'S4', scenario_name:'Optional Column Removed (ip_address)',         expected:'ALLOW', baseline:'BLOCK', sentinel:'ALLOW', baseline_correct:false, sentinel_correct:true },
    { scenario_id:'S5', scenario_name:'Nullable Constraint Changed',                  expected:'BLOCK', baseline:'ALLOW', sentinel:'BLOCK', baseline_correct:false, sentinel_correct:true },
    { scenario_id:'S6', scenario_name:'Non-Breaking Column Addition',                  expected:'ALLOW', baseline:'ALLOW', sentinel:'ALLOW', baseline_correct:true,  sentinel_correct:true },
    { scenario_id:'S7', scenario_name:'Empty Schema Payload (fail-closed)',            expected:'BLOCK', baseline:'ALLOW', sentinel:'BLOCK', baseline_correct:false, sentinel_correct:true },
    { scenario_id:'S8', scenario_name:'Duplicate Column Names',                        expected:'BLOCK', baseline:'ALLOW', sentinel:'BLOCK', baseline_correct:false, sentinel_correct:true },
    { scenario_id:'S9', scenario_name:'Primary Key Removed',                           expected:'BLOCK', baseline:'BLOCK', sentinel:'BLOCK', baseline_correct:true,  sentinel_correct:true },
    { scenario_id:'S10',scenario_name:'datetime → date (Precision Loss)',              expected:'BLOCK', baseline:'ALLOW', sentinel:'BLOCK', baseline_correct:false, sentinel_correct:true },
  ]
};

function ExperimentPage() {
  return (
    <div>
      <div className="page-header">
        <h1>🧪 Experiment Results</h1>
        <p>Measured comparison: Baseline (naive diff) vs Sentinel (this system)</p>
      </div>
      <div className="page-content">
        <div className="grid-2 section-gap">
          <div className="stat-card">
            <div className="stat-label">📊 Baseline Accuracy</div>
            <div className="stat-value" style={{ color:'var(--danger)' }}>{EXP_DATA.baseline_accuracy_pct}%</div>
            <div className="stat-sub">4/10 scenarios correct</div>
            <div className="metric-bar" style={{marginTop:8}}>
              <div className="metric-bar-fill" style={{ width:`${EXP_DATA.baseline_accuracy_pct}%`, background:'var(--danger)' }} />
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">🛡️ Sentinel Accuracy</div>
            <div className="stat-value" style={{ color:'var(--success)' }}>{EXP_DATA.sentinel_accuracy_pct}%</div>
            <div className="stat-sub">10/10 scenarios correct</div>
            <div className="metric-bar" style={{marginTop:8}}>
              <div className="metric-bar-fill" style={{ width:`${EXP_DATA.sentinel_accuracy_pct}%`, background:'var(--success)' }} />
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">⚠️ Baseline Unsafe Rate</div>
            <div className="stat-value" style={{ color:'var(--danger)' }}>{EXP_DATA.baseline_unsafe_pub_rate_pct}%</div>
            <div className="stat-sub">Breaking changes published silently</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">✅ Sentinel Unsafe Rate</div>
            <div className="stat-value" style={{ color:'var(--success)' }}>{EXP_DATA.sentinel_unsafe_pub_rate_pct}%</div>
            <div className="stat-sub">{EXP_DATA.improvement_percentage_points}pp improvement</div>
          </div>
        </div>

        <div className="card section-gap">
          <div className="card-title" style={{marginBottom:12}}>Error Analysis — Why the Baseline Fails</div>
          <div style={{ fontSize:13, color:'var(--text-secondary)', lineHeight:1.8 }}>
            <p>The naive baseline only detects <strong style={{color:'var(--text-primary)'}}>column removal by name</strong>. It misses:</p>
            <ul style={{ paddingLeft:20 }}>
              <li>🔴 <strong>Type changes</strong> (e.g. decimal→string) — no type awareness</li>
              <li>🔴 <strong>Nullable constraint relaxation</strong> — no constraint metadata checked</li>
              <li>🔴 <strong>Empty payload</strong> — baseline allows empty payloads silently (no fail-closed)</li>
              <li>🔴 <strong>Duplicate columns</strong> — no structural validation</li>
              <li>🔴 <strong>Precision loss</strong> (datetime→date) — treats types as strings</li>
              <li>🟡 <strong>False positives</strong>: flags optional column removal as BLOCK (too aggressive)</li>
            </ul>
            <p>The sentinel uses a <strong style={{color:'var(--text-primary)'}}>type-compatibility matrix</strong>, <strong style={{color:'var(--text-primary)'}}>nullability metadata</strong>, 
               <strong style={{color:'var(--text-primary)'}}> PK tracking</strong>, and a <strong style={{color:'var(--text-primary)'}}>fail-closed gate</strong> to correctly classify all change types.</p>
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Scenario</th>
                <th>Expected</th>
                <th>Baseline</th>
                <th>Sentinel</th>
                <th>Baseline ✓</th>
                <th>Sentinel ✓</th>
              </tr>
            </thead>
            <tbody>
              {EXP_DATA.scenarios.map(s => (
                <tr key={s.scenario_id} className={s.sentinel_correct ? 'experiment-row-correct' : 'experiment-row-wrong'}>
                  <td><span className="mono">{s.scenario_id}</span> {s.scenario_name}</td>
                  <td>{decisionBadge(s.expected)}</td>
                  <td>{decisionBadge(s.baseline)}</td>
                  <td>{decisionBadge(s.sentinel)}</td>
                  <td>{s.baseline_correct ? '✅' : '❌'}</td>
                  <td>{s.sentinel_correct ? '✅' : '❌'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ─── Admin Panel ───────────────────────────────────────────────────────────────
function AdminPage({ user }) {
  const [tab, setTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [partners, setPartners] = useState([]);
  const [orgs, setOrgs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getUsers(), api.getPartners(), api.getOrganisations()])
      .then(([u, p, o]) => { setUsers(u); setPartners(p); setOrgs(o); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>⚙️ Admin Panel</h1>
        <p>Organisation, partner, and user management</p>
      </div>
      <div className="page-content">
        <div className="tab-bar">
          {['users','partners','organisations'].map(t => (
            <button key={t} className={`tab-btn ${tab===t?'active':''}`} onClick={() => setTab(t)}>
              {t.charAt(0).toUpperCase()+t.slice(1)}
            </button>
          ))}
        </div>
        {loading ? <div style={{ textAlign:'center', padding:40 }}><span className="spinner" /></div> : (
          <>
            {tab === 'users' && (
              <div className="table-wrapper">
                <table>
                  <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Org</th></tr></thead>
                  <tbody>
                    {users.map(u => (
                      <tr key={u.id}>
                        <td style={{ fontWeight:500 }}>{u.full_name}</td>
                        <td className="mono">{u.email}</td>
                        <td>{roleBadge(u.role)}</td>
                        <td className="mono" style={{ fontSize:11 }}>{u.organisation_id.slice(0,12)}...</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {tab === 'partners' && (
              <div className="table-wrapper">
                <table>
                  <thead><tr><th>Name</th><th>Email</th><th>Status</th><th>Created</th></tr></thead>
                  <tbody>
                    {partners.map(p => (
                      <tr key={p.id}>
                        <td style={{ fontWeight:500 }}>{p.name}</td>
                        <td>{p.contact_email || '—'}</td>
                        <td><span className={`badge ${p.status==='ACTIVE'?'badge-allow':'badge-warning'}`}>{p.status}</span></td>
                        <td>{fmtDate(p.created_at).split(',')[0]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {tab === 'organisations' && (
              <div className="table-wrapper">
                <table>
                  <thead><tr><th>Name</th><th>Description</th><th>Active</th><th>Created</th></tr></thead>
                  <tbody>
                    {orgs.map(o => (
                      <tr key={o.id}>
                        <td style={{ fontWeight:500 }}>{o.name}</td>
                        <td>{o.description || '—'}</td>
                        <td>{o.is_active ? '✅' : '❌'}</td>
                        <td>{fmtDate(o.created_at).split(',')[0]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ─── App Root ─────────────────────────────────────────────────────────────────
export default function App() {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('scs_user') || 'null'); } catch { return null; }
  });
  const [page, setPage] = useState('dashboard');
  const [toasts, setToasts] = useState([]);

  const addToast = (msg, type='success') => {
    const id = Date.now();
    setToasts(t => [...t, { id, msg, type }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3000);
  };

  const handleLogin = (u) => { setUser(u); addToast(`Welcome, ${u.full_name}!`); };
  const handleLogout = () => { clearToken(); setUser(null); setPage('dashboard'); };

  // Verify token still valid
  useEffect(() => {
    if (user && getToken()) {
      api.health().catch(() => { clearToken(); setUser(null); });
    }
  }, []);

  if (!user) return <LoginPage onLogin={handleLogin} />;

  const pages = {
    dashboard: <Dashboard user={user} />,
    scenarios: <ScenariosPage />,
    schemas:   <SchemasPage />,
    runs:      <RunsPage />,
    audit:     <AuditPage />,
    validate:  <ValidatePage />,
    experiment:<ExperimentPage />,
    admin:     <AdminPage user={user} />,
  };

  return (
    <div className="app-shell">
      <Sidebar page={page} setPage={setPage} user={user} onLogout={handleLogout} />
      <main className="main-content">
        {pages[page] || pages.dashboard}
      </main>
      <Toast toasts={toasts} />
    </div>
  );
}
