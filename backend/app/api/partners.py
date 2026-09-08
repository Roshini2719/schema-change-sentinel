from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models import Partner, User
from app.schemas.partner import PartnerCreate, PartnerResponse
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/api/partners", tags=["partners"])

@router.get("/", response_model=List[PartnerResponse])
def list_partners(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Partner).filter(Partner.organization_id == current_user.organization_id).all()

@router.post("/", response_model=PartnerResponse)
def create_partner(
    partner: PartnerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DATA_ENGINEER"]))
):
    db_partner = Partner(**partner.dict(), organization_id=current_user.organization_id)
    db.add(db_partner)
    db.commit()
    db.refresh(db_partner)
    log_audit_event(db, current_user.id, current_user.organization_id, "CREATE_PARTNER", f"Created partner {db_partner.name}")
    return db_partner
