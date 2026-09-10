import { PipelineMetric, DataSource, SchemaContract, PipelineRun, DependencyImpact, AuditLog } from '../types';

const API_BASE = '/api';

export const mockMetrics: PipelineMetric = {
  total_evaluations: 1428,
  total_allowed: 1104,
  total_warned: 240,
  total_blocked: 84,
  breaking_changes_detected: 128,
  active_contracts: 42,
};

export const mockDataSources: DataSource[] = [
  { id: 1, name: 'stripe_payments_stream', partner_name: 'Stripe Gateway', source_type: 'PostgreSQL / CDC', status: 'ACTIVE', last_evaluated: '2026-09-10T09:30:00Z' },
  { id: 2, name: 'plaid_transactions_v2', partner_name: 'Plaid Open Banking', source_type: 'Kafka / JSON', status: 'ACTIVE', last_evaluated: '2026-09-10T09:25:00Z' },
  { id: 3, name: 'checkout_orders_feed', partner_name: 'Checkout.com', source_type: 'Webhook Payload', status: 'WARN', last_evaluated: '2026-09-10T09:12:00Z' },
  { id: 4, name: 'kyc_verification_logs', partner_name: 'Jumio KYC', source_type: 'Snowflake External Table', status: 'ACTIVE', last_evaluated: '2026-09-10T08:50:00Z' },
];

export const mockContracts: SchemaContract[] = [
  {
    id: 101,
    data_source_id: 1,
    version: 'v2.4.0',
    status: 'ACTIVE',
    strict_mode: true,
    required_fields: ['transaction_id', 'amount', 'currency', 'account_number', 'timestamp'],
    allowed_types: { amount: 'DECIMAL(18,4)', currency: 'VARCHAR(3)', account_number: 'VARCHAR(64)' },
    created_at: '2026-08-15T10:00:00Z'
  },
  {
    id: 102,
    data_source_id: 2,
    version: 'v1.9.1',
    status: 'ACTIVE',
    strict_mode: true,
    required_fields: ['item_id', 'account_id', 'amount', 'date', 'category_id'],
    allowed_types: { amount: 'FLOAT', date: 'DATE' },
    created_at: '2026-08-20T14:30:00Z'
  }
];

export const mockPipelineRuns: PipelineRun[] = [
  { id: 901, pipeline_id: 'pipe-stripe-001', data_source_id: 1, partner: 'Stripe', status: 'ALLOW', breaking_changes: 0, timestamp: '2026-09-10 09:30:15', execution_time_ms: 145 },
  { id: 902, pipeline_id: 'pipe-plaid-088', data_source_id: 2, partner: 'Plaid', status: 'BLOCK', breaking_changes: 3, timestamp: '2026-09-10 09:25:02', execution_time_ms: 312, details: 'Type mismatch on field `amount` (expected FLOAT, received STRING) and missing required field `category_id`' },
  { id: 903, pipeline_id: 'pipe-chkout-104', data_source_id: 3, partner: 'Checkout', status: 'WARN', breaking_changes: 1, timestamp: '2026-09-10 09:12:44', execution_time_ms: 198, details: 'Deprecated field `card_type` accessed by 2 downstream dbt models' },
  { id: 904, pipeline_id: 'pipe-jumio-044', data_source_id: 4, partner: 'Jumio', status: 'ALLOW', breaking_changes: 0, timestamp: '2026-09-10 08:50:11', execution_time_ms: 92 },
];

export const mockDependencies: DependencyImpact[] = [
  { id: 1, model_name: 'fct_daily_reconciliation', table_type: 'DBT Incremental Model', downstream_depth: 1, risk_level: 'CRITICAL', impacted_columns: ['amount', 'currency'] },
  { id: 2, model_name: 'dim_customer_accounts', table_type: 'Snowflake View', downstream_depth: 2, risk_level: 'HIGH', impacted_columns: ['account_number'] },
  { id: 3, model_name: 'rpt_executive_cashflow', table_type: 'Tableau Data Extract', downstream_depth: 3, risk_level: 'MEDIUM', impacted_columns: ['transaction_id'] },
  { id: 4, model_name: 'stg_raw_partner_events', table_type: 'Staging Table', downstream_depth: 0, risk_level: 'LOW', impacted_columns: ['created_at'] },
];

export const mockAuditLogs: AuditLog[] = [
  { id: 501, timestamp: '2026-09-10 09:25:02', event: 'EVALUATE_SCHEMA', user: 'Sentinel Daemon', decision: 'BLOCK', reason: 'Enforced contract rule #102 violation - null values detected in non-nullable field' },
  { id: 502, timestamp: '2026-09-10 09:12:44', event: 'PUBLISH_OVERRIDE', user: 'Sarah Chen (Lead DE)', decision: 'ALLOW_OVERRIDE', reason: 'Approved deprecation grace period for field card_type' },
  { id: 503, timestamp: '2026-09-10 08:30:11', event: 'CONTRACT_UPDATE', user: 'Alex Rivera (Data Architect)', decision: 'UPDATE_CONTRACT', reason: 'Promoted schema contract to v2.4.0' },
];

export async function fetchMetrics(): Promise<PipelineMetric> {
  try {
    const token = localStorage.getItem('token');
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/metrics/`, { headers });
    if (res.ok) {
      const data = await res.json();
      return {
        total_evaluations: data.total_pipeline_runs || mockMetrics.total_evaluations,
        total_allowed: data.allowed_publications || mockMetrics.total_allowed,
        total_warned: mockMetrics.total_warned,
        total_blocked: data.blocked_publications || mockMetrics.total_blocked,
        breaking_changes_detected: data.total_changes || mockMetrics.breaking_changes_detected,
        active_contracts: data.total_contracts || mockMetrics.active_contracts,
      };
    }
  } catch (e) {
    console.warn('Backend connection falling back to mock metrics:', e);
  }
  return mockMetrics;
}

export async function fetchPipelineRuns(): Promise<PipelineRun[]> {
  try {
    const token = localStorage.getItem('token');
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/pipeline-runs/`, { headers });
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn('Backend connection falling back to mock pipeline runs:', e);
  }
  return mockPipelineRuns;
}
