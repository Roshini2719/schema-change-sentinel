from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models.models import get_db, DataSchema, SchemaColumn, DownstreamDependency, Organisation, Partner
from ..core.auth import get_current_user, require_roles, Roles, UserContext
from ..schemas.schemas import DataSchemaCreate, DataSchemaResponse, DependencyCreate, DependencyResponse

router = APIRouter(prefix="/api/schemas", tags=["schemas"])

@router.get("", response_model=List[DataSchemaResponse])
def list_schemas(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """
    List all schemas visible to the current user.
    - PARTNER role: only sees schemas for their partner
    - Others: see all schemas for their organisation
    """
    q = db.query(DataSchema).filter(DataSchema.organisation_id == current_user.organisation_id)
    if current_user.role == Roles.PARTNER.value and current_user.partner_id:
        q = q.filter(DataSchema.partner_id == current_user.partner_id)
    return q.all()

@router.get("/{schema_id}", response_model=DataSchemaResponse)
def get_schema(
    schema_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    schema = db.query(DataSchema).filter(
        DataSchema.id == schema_id,
        DataSchema.organisation_id == current_user.organisation_id,
    ).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    return schema

@router.post("", response_model=DataSchemaResponse, status_code=201)
def create_schema(
    body: DataSchemaCreate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(require_roles(Roles.ADMIN, Roles.DATA_ENGINEER)),
):
    # Validate partner belongs to org
    partner = db.query(Partner).filter(
        Partner.id == body.partner_id,
        Partner.organisation_id == current_user.organisation_id,
    ).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found in your organisation")

    schema = DataSchema(
        name=body.name,
        version=body.version,
        partner_id=body.partner_id,
        organisation_id=current_user.organisation_id,
        created_by=current_user.email,
    )
    db.add(schema)
    db.flush()

    for col_data in body.columns:
        col = SchemaColumn(schema_id=schema.id, **col_data.model_dump())
        db.add(col)

    db.commit()
    db.refresh(schema)
    return schema

@router.get("/{schema_id}/dependencies", response_model=List[DependencyResponse])
def list_dependencies(
    schema_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    schema = db.query(DataSchema).filter(
        DataSchema.id == schema_id,
        DataSchema.organisation_id == current_user.organisation_id,
    ).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    return db.query(DownstreamDependency).filter(DownstreamDependency.schema_id == schema_id).all()

@router.post("/{schema_id}/dependencies", response_model=DependencyResponse, status_code=201)
def add_dependency(
    schema_id: str,
    body: DependencyCreate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(require_roles(Roles.ADMIN, Roles.DATA_ENGINEER)),
):
    schema = db.query(DataSchema).filter(
        DataSchema.id == schema_id,
        DataSchema.organisation_id == current_user.organisation_id,
    ).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")

    dep = DownstreamDependency(
        schema_id=schema_id,
        organisation_id=current_user.organisation_id,
        consumer_name=body.consumer_name,
        consumer_type=body.consumer_type,
        query_snippet=body.query_snippet,
        columns_used=body.columns_used,
        criticality=body.criticality,
        owner_email=body.owner_email,
    )
    db.add(dep)
    db.commit()
    db.refresh(dep)
    return dep
