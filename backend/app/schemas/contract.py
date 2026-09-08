from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ContractCreate(BaseModel):
    data_source_id: int
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(default="1.0")
    contract_json: Dict[str, Any]


class ContractResponse(BaseModel):
    id: int
    organization_id: int
    data_source_id: int
    name: str
    version: str
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContractValidationResult(BaseModel):
    valid: bool
    violations: List[Dict[str, Any]] = []
