from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.models import get_db, Organisation, Partner, User
from ..core.auth import get_current_user, require_roles, Roles, UserContext
from ..schemas.schemas import (
    OrganisationCreate, OrganisationResponse,
    PartnerCreate, PartnerResponse,
    UserCreate, UserResponse,
)
from ..core.auth import get_password_hash

router = APIRouter(prefix="/api/admin", tags=["admin"])

# ─── Organisations ────────────────────────────────────────────────────────────

@router.get("/organisations", response_model=List[OrganisationResponse])
def list_orgs(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(require_roles(Roles.ADMIN)),
):
    return db.query(Organisation).all()

@router.post("/organisations", response_model=OrganisationResponse, status_code=201)
def create_org(
    body: OrganisationCreate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(require_roles(Roles.ADMIN)),
):
    if db.query(Organisation).filter(Organisation.name == body.name).first():
        raise HTTPException(status_code=400, detail="Organisation name already exists")
    org = Organisation(name=body.name, description=body.description)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

# ─── Partners ─────────────────────────────────────────────────────────────────

@router.get("/partners", response_model=List[PartnerResponse])
def list_partners(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(require_roles(Roles.ADMIN, Roles.DATA_ENGINEER)),
):
    return db.query(Partner).filter(Partner.organisation_id == current_user.organisation_id).all()

@router.post("/partners", response_model=PartnerResponse, status_code=201)
def create_partner(
    body: PartnerCreate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(require_roles(Roles.ADMIN)),
):
    p = Partner(
        name=body.name,
        organisation_id=current_user.organisation_id,
        contact_email=body.contact_email,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

# ─── Users ────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(require_roles(Roles.ADMIN)),
):
    return db.query(User).filter(User.organisation_id == current_user.organisation_id).all()

@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(require_roles(Roles.ADMIN)),
):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    u = User(
        email=body.email,
        hashed_password=get_password_hash(body.password),
        full_name=body.full_name,
        role=body.role,
        organisation_id=current_user.organisation_id,
        partner_id=body.partner_id,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
