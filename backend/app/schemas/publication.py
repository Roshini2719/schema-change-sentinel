from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class PublicationCheckRequest(BaseModel):
    data_source_id: int
    new_schema: Dict[str, Any]


class PublicationCheckResponse(BaseModel):
    decision: str  # ALLOW, WARN, BLOCK
    risk_score: float
    severity: str
    changes: List[Dict[str, Any]] = []
    contract_violations: List[Dict[str, Any]] = []
    affected_dependencies: List[Dict[str, Any]] = []
    pipeline_issues: List[Dict[str, Any]] = []
    reasons: List[str] = []


class PublicationApproveRequest(BaseModel):
    data_source_id: int
    schema_version_id: int


class PublicationOverrideRequest(BaseModel):
    data_source_id: int
    schema_version_id: int
    reason: str = Field(..., min_length=10, description="Reason for override (min 10 chars)")
    confirmation: bool = Field(..., description="Must be true to confirm override")


class PublicationDecisionResponse(BaseModel):
    id: int
    organization_id: int
    data_source_id: int
    schema_version_id: Optional[int] = None
    decision: str
    risk_score: float
    reason: Optional[str] = None
    decided_by: Optional[str] = None
    override_reason: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
