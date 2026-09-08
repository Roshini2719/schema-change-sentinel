from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class OrganizationResponse(BaseModel):
    id: int
    name: str
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
