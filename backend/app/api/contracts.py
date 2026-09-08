from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models import DataContract, DataSource, User
from app.schemas.contract import ContractCreate, ContractResponse
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/api/contracts", tags=["contracts"])

@router.get("/", response_model=List[ContractResponse])
def list_contracts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(DataContract).join(DataSource).filter(DataSource.organization_id == current_user.organization_id).all()

@router.post("/", response_model=ContractResponse)
def create_contract(
    contract: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DATA_ENGINEER"]))
):
    data_source = db.query(DataSource).filter(
        DataSource.id == contract.data_source_id,
        DataSource.organization_id == current_user.organization_id
    ).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    db_contract = DataContract(**contract.dict())
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    log_audit_event(db, current_user.id, current_user.organization_id, "CREATE_CONTRACT", f"Created contract for DS {db_contract.data_source_id}")
    return db_contract
