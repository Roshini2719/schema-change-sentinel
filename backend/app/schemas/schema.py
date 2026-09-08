from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class SchemaFieldInfo(BaseModel):
    type: str
    required: bool = True
    nullable: bool = False
    primary_key: bool = False
    default_value: Optional[str] = None
    values: Optional[List[str]] = None  # for enum types


class SchemaRegisterRequest(BaseModel):
    data_source_id: int
    version: str = Field(..., min_length=1)
    schema_json: Dict[str, Any]


class SchemaCompareRequest(BaseModel):
    data_source_id: int
    new_schema: Dict[str, Any]


class SchemaValidateRequest(BaseModel):
    data_source_id: int
    schema_json: Dict[str, Any]


class SchemaFieldResponse(BaseModel):
    id: int
    field_name: str
    data_type: str
    nullable: bool
    required: bool
    default_value: Optional[str] = None
    is_primary_key: bool
    enum_values: Optional[str] = None

    class Config:
        from_attributes = True


class SchemaVersionResponse(BaseModel):
    id: int
    data_source_id: int
    version: str
    schema_hash: str
    status: str
    created_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    fields: List[SchemaFieldResponse] = []

    class Config:
        from_attributes = True


class ChangeDetail(BaseModel):
    field: str
    change_type: str
    severity: str
    reason: str
    old_type: Optional[str] = None
    new_type: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None


class SchemaCompareResponse(BaseModel):
    breaking: bool
    severity: str
    risk_score: float
    changes: List[ChangeDetail]
