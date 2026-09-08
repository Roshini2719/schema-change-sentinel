from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.dependencies import get_current_user, require_admin
from app.models import Organization, User
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/api/organizations", tags=["organizations"])

@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "ADMIN":
        return db.query(Organization).all()
    return db.query(Organization).filter(Organization.id == current_user.organization_id).all()

@router.post("/", response_model=OrganizationResponse)
def create_organization(
    org: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    db_org = Organization(**org.dict())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    log_audit_event(db, current_user.id, current_user.organization_id, "CREATE_ORGANIZATION", f"Created organization {db_org.name}")
    return db_org
