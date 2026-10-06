import os

PROJECT_ROOT = "/Users/muthamilroshini/.gemini/antigravity/scratch/schema-sentinel"

FILES = {}
FILES["backend/app/schemas/__init__.py"] = ""

FILES["backend/app/schemas/schemas.py"] = """
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime
from uuid import uuid4

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

class SchemaColumnCreate(BaseModel):
    column_name: str
    data_type: str
    is_nullable: bool = False
    is_required: bool = True
    is_primary_key: bool = False
    format_pattern: Optional[str] = None
    description: Optional[str] = None

class SchemaColumnResponse(SchemaColumnCreate):
    id: str
    schema_id: str
    order_index: int
    model_config = ConfigDict(from_attributes=True)

class SchemaCreate(BaseModel):
    partner_id: str
    schema_name: str
    version: int
    columns: List[SchemaColumnCreate]

class SchemaResponse(BaseModel):
    id: str
    organisation_id: str
    partner_id: str
    schema_name: str
    version: int
    status: str
    created_at: datetime
    columns: Optional[List[SchemaColumnResponse]] = None
    model_config = ConfigDict(from_attributes=True)

class SchemaCompareRequest(BaseModel):
    expected_schema_id: str
    incoming_columns: List[dict]

class SchemaChangeResponse(BaseModel):
    id: Optional[str] = None
    change_type: str
    column_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    severity: str
    category: str
    reason: str
    recommendation: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class SchemaCompareResponse(BaseModel):
    changes: List[SchemaChangeResponse]
    has_breaking_changes: bool
    publication_decision: str
    affected_dependencies: int

class ContractRuleCreate(BaseModel):
    column_name: str
    data_type: str
    is_required: bool = True
    is_nullable: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[str] = None
    regex_pattern: Optional[str] = None
    description: Optional[str] = None

class ContractRuleResponse(ContractRuleCreate):
    id: str
    contract_id: str
    model_config = ConfigDict(from_attributes=True)

class DataContractCreate(BaseModel):
    partner_id: str
    contract_name: str
    version: int = 1
    rules: List[ContractRuleCreate]

class DataContractResponse(BaseModel):
    id: str
    organisation_id: str
    partner_id: str
    contract_name: str
    version: int
    status: str
    created_at: datetime
    rules: Optional[List[ContractRuleResponse]] = None
    model_config = ConfigDict(from_attributes=True)

class PipelineRunCreate(BaseModel):
    partner_id: str
    schema_version: int
    records_received: int
    incoming_columns: List[dict]
    record_data: Optional[List[dict]] = None

class PipelineRunResponse(BaseModel):
    id: str
    organisation_id: str
    partner_id: str
    schema_version: int
    received_at: datetime
    status: str
    publication_status: str
    failure_reason: Optional[str] = None
    is_baseline: bool
    model_config = ConfigDict(from_attributes=True)

class PipelineRunDetailResponse(PipelineRunResponse):
    changes: List[SchemaChangeResponse]
    dependencies_affected: int
    publication_decision: str

class DependencyColumnCreate(BaseModel):
    column_name: str
    is_critical: bool = True

class DependencyColumnResponse(DependencyColumnCreate):
    id: str
    dependency_id: str
    model_config = ConfigDict(from_attributes=True)

class DependencyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    owner: Optional[str] = None
    criticality: str = 'MEDIUM'
    columns: List[DependencyColumnCreate]

class DependencyResponse(BaseModel):
    id: str
    organisation_id: str
    name: str
    description: Optional[str] = None
    owner: Optional[str] = None
    criticality: str
    created_at: datetime
    columns: Optional[List[DependencyColumnResponse]] = None
    model_config = ConfigDict(from_attributes=True)

class AlertResponse(BaseModel):
    id: str
    organisation_id: str
    pipeline_run_id: Optional[str] = None
    severity: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AuditLogResponse(BaseModel):
    id: str
    organisation_id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class FeedbackCreate(BaseModel):
    respondent_role: str
    clarity_score: int
    usefulness_score: int
    schema_diff_clarity: int
    dashboard_helpfulness: int
    risk_reduction_confidence: int
    suggestions: Optional[str] = None

class FeedbackResponse(FeedbackCreate):
    id: str
    organisation_id: Optional[str] = None
    is_simulated: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class FeedbackSummaryResponse(BaseModel):
    average_clarity: float
    average_usefulness: float
    average_schema_diff_clarity: float
    average_dashboard_helpfulness: float
    average_risk_reduction: float
    total_responses: int

class DashboardMetrics(BaseModel):
    total_runs: int
    successful_runs: int
    blocked_runs: int
    breaking_changes: int
    affected_consumers: int
    total_partners: int
    total_organisations: int
    recent_alerts: List[AlertResponse]
    runs_over_time: List[dict]
    changes_by_severity: dict

class DemoScenarioRequest(BaseModel):
    scenario: str

class DemoScenarioResponse(BaseModel):
    run_id: str
    status: str
    changes: List[SchemaChangeResponse]
    affected_dependencies: int
    publication_decision: str

class PublicationOverrideRequest(BaseModel):
    pipeline_run_id: str
    justification: str

class BaselineCompareResponse(BaseModel):
    run_id: str
    status: str
    publication_decision: str
    message: str
""".strip()

def main():
    for rel_path, content in FILES.items():
        full_path = os.path.join(PROJECT_ROOT, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
    print("Scaffold 2 complete.")

if __name__ == "__main__":
    main()
