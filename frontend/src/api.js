// API client for Schema Change Sentinel backend
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

let _token = localStorage.getItem('scs_token') || null;

export function setToken(t) { _token = t; localStorage.setItem('scs_token', t); }
export function clearToken() { _token = null; localStorage.removeItem('scs_token'); localStorage.removeItem('scs_user'); }
export function getToken() { return _token; }

async function request(method, path, body = null) {
  const headers = { 'Content-Type': 'application/json' };
  if (_token) headers['Authorization'] = `Bearer ${_token}`;
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 401) { clearToken(); window.location.reload(); }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
}

export const api = {
  login: (email, password) => request('POST', '/api/auth/login', { email, password }),
  health: () => request('GET', '/health'),

  // Schemas
  getSchemas: () => request('GET', '/api/schemas'),
  getSchema: (id) => request('GET', `/api/schemas/${id}`),
  getDependencies: (schemaId) => request('GET', `/api/schemas/${schemaId}/dependencies`),

  // Validation
  validate: (body) => request('POST', '/api/validate', body),
  getPipelineRuns: () => request('GET', '/api/pipeline-runs'),

  // Audit
  getAuditLogs: (action) => request('GET', `/api/audit${action ? `?action=${action}` : ''}`),

  // Admin
  getOrganisations: () => request('GET', '/api/admin/organisations'),
  getPartners: () => request('GET', '/api/admin/partners'),
  getUsers: () => request('GET', '/api/admin/users'),

  // Demo
  getScenarios: () => request('GET', '/api/demo/scenarios'),
  runScenario: (id) => request('POST', `/api/demo/scenarios/${id}/run`),
};
