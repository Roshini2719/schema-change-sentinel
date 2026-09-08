from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DataSourceCreate(BaseModel):
    partner_id: int
    name: str = Field(..., min_length=1, max_length=255)
    source_type: str = Field(default="transaction")
    description: Optional[str] = None


class DataSourceResponse(BaseModel):
    id: int
    organization_id: int
    partner_id: int
    name: str
    source_type: str
    description: Optional[str] = None
    current_schema_version: Optional[int] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
