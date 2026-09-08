from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models import DownstreamDependency, DependencyField, DataSource, User
from app.schemas.dependency import DependencyCreate, DependencyResponse
from app.services.dependency_analyzer import extract_fields_from_query
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/api/dependencies", tags=["dependencies"])

@router.get("/", response_model=List[DependencyResponse])
def list_dependencies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(DownstreamDependency).filter(DownstreamDependency.organization_id == current_user.organization_id).all()

@router.post("/", response_model=DependencyResponse)
def create_dependency(
    dep: DependencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DATA_ENGINEER"]))
):
    data_source = db.query(DataSource).filter(
        DataSource.id == dep.data_source_id,
        DataSource.organization_id == current_user.organization_id
    ).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    db_dep = DownstreamDependency(
        data_source_id=dep.data_source_id,
        organization_id=current_user.organization_id,
        dependency_name=dep.dependency_name,
        dependency_type=dep.dependency_type,
        query_text=dep.query_text
    )
    db.add(db_dep)
    db.commit()
    db.refresh(db_dep)

    fields_to_add = dep.fields if dep.fields else []
    if dep.query_text:
        extracted = extract_fields_from_query(dep.query_text)
        fields_to_add.extend(extracted)
    
    # Deduplicate fields
    unique_fields = list(set(fields_to_add))
    
    for field_name in unique_fields:
        df = DependencyField(dependency_id=db_dep.id, field_name=field_name)
        db.add(df)
    
    db.commit()
    db.refresh(db_dep)
    
    log_audit_event(db, current_user.id, current_user.organization_id, "CREATE_DEPENDENCY", f"Created dependency {db_dep.dependency_name}")
    return db_dep
