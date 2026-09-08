from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class DependencyFieldCreate(BaseModel):
    field_name: str


class DependencyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    dependency_type: str = Field(default="query")
    query_text: Optional[str] = None
    target_table: Optional[str] = None
    criticality: str = Field(default="medium")
    owner: Optional[str] = None
    fields: List[DependencyFieldCreate] = []


class DependencyFieldResponse(BaseModel):
    id: int
    field_name: str

    class Config:
        from_attributes = True


class DependencyResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    dependency_type: str
    query_text: Optional[str] = None
    target_table: Optional[str] = None
    criticality: str
    owner: Optional[str] = None
    created_at: Optional[datetime] = None
    fields: List[DependencyFieldResponse] = []

    class Config:
        from_attributes = True


class DependencyAnalysisResult(BaseModel):
    affected_dependencies: List[Dict] = []
    total_affected: int = 0
    has_critical: bool = False
