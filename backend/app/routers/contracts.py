from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.connection import get_db
from ..models.models import DataContract, ContractRule
from ..schemas.schemas import DataContractCreate, DataContractResponse
from ..core.auth import get_current_user, UserContext, role_required, Roles

router = APIRouter(prefix="/api/contracts", tags=["contracts"])

@router.get("", response_model=List[DataContractResponse])
def list_contracts(
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contracts = db.query(DataContract).filter(DataContract.organisation_id == current_user.organisation_id).all()
    res = []
    for c in contracts:
        rules = db.query(ContractRule).filter(ContractRule.contract_id == c.id).all()
        res.append({
            "id": c.id,
            "organisation_id": c.organisation_id,
            "partner_id": c.partner_id,
            "contract_name": c.contract_name,
            "version": c.version,
            "status": c.status,
            "created_at": c.created_at,
            "rules": rules
        })
    return res

@router.post("", response_model=DataContractResponse)
def create_contract(
    req: DataContractCreate,
    current_user: UserContext = Depends(role_required([Roles.ADMIN, Roles.DATA_ENGINEER])),
    db: Session = Depends(get_db)
):
    contract = DataContract(
        organisation_id=current_user.organisation_id,
        partner_id=req.partner_id,
        contract_name=req.contract_name,
        version=req.version,
        created_by=current_user.user_id
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)

    created_rules = []
    for r in req.rules:
        r_obj = ContractRule(
            contract_id=contract.id,
            column_name=r.column_name,
            data_type=r.data_type,
            is_required=r.is_required,
            is_nullable=r.is_nullable,
            min_value=r.min_value,
            max_value=r.max_value,
            allowed_values=r.allowed_values,
            regex_pattern=r.regex_pattern,
            description=r.description
        )
        db.add(r_obj)
        created_rules.append(r_obj)

    db.commit()

    return {
        "id": contract.id,
        "organisation_id": contract.organisation_id,
        "partner_id": contract.partner_id,
        "contract_name": contract.contract_name,
        "version": contract.version,
        "status": contract.status,
        "created_at": contract.created_at,
        "rules": created_rules
    }
