export interface PipelineMetric {
  total_evaluations: number;
  total_allowed: number;
  total_warned: number;
  total_blocked: number;
  breaking_changes_detected: number;
  active_contracts: number;
}

export interface DataSource {
  id: number;
  name: string;
  partner_name: string;
  source_type: string;
  status: string;
  last_evaluated: string;
}

export interface SchemaContract {
  id: number;
  data_source_id: number;
  version: string;
  status: string;
  strict_mode: boolean;
  required_fields: string[];
  allowed_types: Record<string, string>;
  created_at: string;
}

export interface PipelineRun {
  id: number;
  pipeline_id: string;
  data_source_id: number;
  partner: string;
  status: 'ALLOW' | 'WARN' | 'BLOCK';
  breaking_changes: number;
  timestamp: string;
  execution_time_ms: number;
  details?: string;
}

export interface DependencyImpact {
  id: number;
  model_name: string;
  table_type: string;
  downstream_depth: number;
  risk_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  impacted_columns: string[];
}

export interface AuditLog {
  id: number;
  timestamp: string;
  event: string;
  user: string;
  decision: string;
  reason: string;
}
