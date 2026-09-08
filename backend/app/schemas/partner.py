from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PartnerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class PartnerResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    description: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
