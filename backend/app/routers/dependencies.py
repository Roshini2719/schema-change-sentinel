from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.connection import get_db
from ..models.models import DownstreamDependency, DependencyColumn
from ..schemas.schemas import DependencyCreate, DependencyResponse
from ..core.auth import get_current_user, UserContext, role_required, Roles

router = APIRouter(prefix="/api/dependencies", tags=["dependencies"])

@router.get("", response_model=List[DependencyResponse])
def list_dependencies(
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deps = db.query(DownstreamDependency).filter(DownstreamDependency.organisation_id == current_user.organisation_id).all()
    res = []
    for d in deps:
        cols = db.query(DependencyColumn).filter(DependencyColumn.dependency_id == d.id).all()
        res.append({
            "id": d.id,
            "organisation_id": d.organisation_id,
            "name": d.name,
            "description": d.description,
            "owner": d.owner,
            "criticality": d.criticality,
            "created_at": d.created_at,
            "columns": cols
        })
    return res

@router.post("", response_model=DependencyResponse)
def create_dependency(
    req: DependencyCreate,
    current_user: UserContext = Depends(role_required([Roles.ADMIN, Roles.DATA_ENGINEER])),
    db: Session = Depends(get_db)
):
    dep = DownstreamDependency(
        organisation_id=current_user.organisation_id,
        name=req.name,
        description=req.description,
        owner=req.owner,
        criticality=req.criticality
    )
    db.add(dep)
    db.commit()
    db.refresh(dep)

    created_cols = []
    for c in req.columns:
        c_obj = DependencyColumn(
            dependency_id=dep.id,
            column_name=c.column_name,
            is_critical=c.is_critical
        )
        db.add(c_obj)
        created_cols.append(c_obj)

    db.commit()

    return {
        "id": dep.id,
        "organisation_id": dep.organisation_id,
        "name": dep.name,
        "description": dep.description,
        "owner": dep.owner,
        "criticality": dep.criticality,
        "created_at": dep.created_at,
        "columns": created_cols
    }
