from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime


# ─── Auth ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    organisation_id: str
    partner_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str
    organisation_id: str
    partner_id: Optional[str] = None


# ─── Organisation / Partner ───────────────────────────────────────────────────

class OrganisationCreate(BaseModel):
    name: str
    description: Optional[str] = None

class OrganisationResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class PartnerCreate(BaseModel):
    name: str
    organisation_id: str
    contact_email: Optional[str] = None

class PartnerResponse(BaseModel):
    id: str
    name: str
    organisation_id: str
    contact_email: Optional[str] = None
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ─── Schema ───────────────────────────────────────────────────────────────────

class SchemaColumnCreate(BaseModel):
    column_name: str
    data_type: str
    is_nullable: bool = False
    is_required: bool = True
    is_primary_key: bool = False
    format_pattern: Optional[str] = None
    description: Optional[str] = None

class SchemaColumnResponse(BaseModel):
    id: str
    column_name: str
    data_type: str
    is_nullable: bool
    is_required: bool
    is_primary_key: bool
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class DataSchemaCreate(BaseModel):
    name: str
    version: str = "1.0.0"
    partner_id: str
    columns: List[SchemaColumnCreate]

class DataSchemaResponse(BaseModel):
    id: str
    name: str
    version: str
    partner_id: str
    organisation_id: str
    is_active: bool
    created_at: datetime
    columns: List[SchemaColumnResponse] = []
    model_config = ConfigDict(from_attributes=True)


# ─── Validation / Gate ────────────────────────────────────────────────────────

class IncomingColumn(BaseModel):
    column_name: str
    data_type: str
    is_nullable: Optional[bool] = None
    is_required: Optional[bool] = None
    is_primary_key: Optional[bool] = None

class ValidateRequest(BaseModel):
    schema_id: str
    incoming_columns: List[IncomingColumn]
    run_label: Optional[str] = None

class SchemaChangeEventResponse(BaseModel):
    change_type: str
    column_name: str
    old_value: Optional[str]
    new_value: Optional[str]
    severity: str
    category: str
    reason: str
    recommendation: str
    affected_consumers: List[str] = []

class GateDecisionResponse(BaseModel):
    decision: str
    reason: str
    pipeline_run_id: str
    breaking_changes: List[SchemaChangeEventResponse]
    warning_changes: List[SchemaChangeEventResponse]
    info_changes: List[SchemaChangeEventResponse]
    affected_consumers: List[str]
    is_fail_closed: bool = False


# ─── Pipeline Runs ────────────────────────────────────────────────────────────

class PipelineRunResponse(BaseModel):
    id: str
    partner_id: str
    organisation_id: str
    schema_id: Optional[str]
    run_timestamp: datetime
    status: str
    gate_decision: Optional[str]
    breaking_changes_count: int
    warning_changes_count: int
    error_message: Optional[str]
    changes_detected: Optional[Any]
    affected_consumers: Optional[Any]
    model_config = ConfigDict(from_attributes=True)


# ─── Audit Log ────────────────────────────────────────────────────────────────

class AuditLogResponse(BaseModel):
    id: str
    organisation_id: str
    user_id: Optional[str]
    user_email: Optional[str]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    details: Optional[Any]
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


# ─── Downstream Dependency ────────────────────────────────────────────────────

class DependencyCreate(BaseModel):
    schema_id: str
    consumer_name: str
    consumer_type: str
    query_snippet: Optional[str] = None
    columns_used: Optional[List[str]] = None
    criticality: str = "HIGH"
    owner_email: Optional[str] = None

class DependencyResponse(BaseModel):
    id: str
    schema_id: str
    organisation_id: str
    consumer_name: str
    consumer_type: str
    columns_used: Optional[List[str]]
    criticality: str
    owner_email: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ─── Experiment ───────────────────────────────────────────────────────────────

class ExperimentResult(BaseModel):
    scenario_id: str
    scenario_name: str
    baseline_decision: str
    sentinel_decision: str
    breaking_changes: int
    warning_changes: int
    baseline_correct: bool
    sentinel_correct: bool
    latency_ms: Optional[float] = None