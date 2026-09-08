from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PipelineRunCreate(BaseModel):
    data_source_id: int
    schema_version_id: Optional[int] = None
    run_id: str = Field(..., min_length=1)
    status: str = Field(default="running")
    expected_records: Optional[int] = None
    records_received: Optional[int] = 0
    records_processed: Optional[int] = 0
    records_rejected: Optional[int] = 0
    error_message: Optional[str] = None


class PipelineRunUpdate(BaseModel):
    status: Optional[str] = None
    records_received: Optional[int] = None
    records_processed: Optional[int] = None
    records_rejected: Optional[int] = None
    error_message: Optional[str] = None


class PipelineRunResponse(BaseModel):
    id: int
    organization_id: int
    data_source_id: int
    schema_version_id: Optional[int] = None
    run_id: str
    status: str
    expected_records: Optional[int] = None
    records_received: Optional[int] = None
    records_processed: Optional[int] = None
    records_rejected: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class PipelineHealthResult(BaseModel):
    healthy: bool
    issues: list = []
    severity: str = "NONE"
