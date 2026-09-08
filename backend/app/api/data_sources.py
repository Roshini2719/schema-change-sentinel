from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models import DataSource, Partner, User
from app.schemas.data_source import DataSourceCreate, DataSourceResponse
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/api/data-sources", tags=["data_sources"])

@router.get("/", response_model=List[DataSourceResponse])
def list_data_sources(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(DataSource).filter(DataSource.organization_id == current_user.organization_id).all()

@router.post("/", response_model=DataSourceResponse)
def create_data_source(
    ds: DataSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DATA_ENGINEER"]))
):
    partner = db.query(Partner).filter(
        Partner.id == ds.partner_id, 
        Partner.organization_id == current_user.organization_id
    ).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
        
    db_ds = DataSource(**ds.dict(), organization_id=current_user.organization_id)
    db.add(db_ds)
    db.commit()
    db.refresh(db_ds)
    log_audit_event(db, current_user.id, current_user.organization_id, "CREATE_DATA_SOURCE", f"Created data source {db_ds.name}")
    return db_ds
