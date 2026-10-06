from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.connection import get_db
from ..models.models import Schema, SchemaColumn, Partner
from ..schemas.schemas import SchemaCreate, SchemaResponse, SchemaCompareRequest, SchemaCompareResponse
from ..core.auth import get_current_user, UserContext, role_required, Roles
from ..services.schema_sentinel import compare_schemas
from ..services.dependency_analyzer import analyze_impact
from ..services.risk_engine import RiskEngine

router = APIRouter(prefix="/api/schemas", tags=["schemas"])

@router.get("", response_model=List[SchemaResponse])
def list_schemas(
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    schemas = db.query(Schema).filter(Schema.organisation_id == current_user.organisation_id).all()
    res = []
    for s in schemas:
        cols = db.query(SchemaColumn).filter(SchemaColumn.schema_id == s.id).order_by(SchemaColumn.order_index).all()
        s_dict = {
            "id": s.id,
            "organisation_id": s.organisation_id,
            "partner_id": s.partner_id,
            "schema_name": s.schema_name,
            "version": s.version,
            "status": s.status,
            "created_at": s.created_at,
            "columns": cols
        }
        res.append(s_dict)
    return res

@router.post("", response_model=SchemaResponse)
def create_schema(
    req: SchemaCreate,
    current_user: UserContext = Depends(role_required([Roles.ADMIN, Roles.DATA_ENGINEER])),
    db: Session = Depends(get_db)
):
    schema_obj = Schema(
        organisation_id=current_user.organisation_id,
        partner_id=req.partner_id,
        schema_name=req.schema_name,
        version=req.version,
        created_by=current_user.user_id
    )
    db.add(schema_obj)
    db.commit()
    db.refresh(schema_obj)

    created_cols = []
    for idx, col in enumerate(req.columns):
        c_obj = SchemaColumn(
            schema_id=schema_obj.id,
            column_name=col.column_name,
            data_type=col.data_type,
            is_nullable=col.is_nullable,
            is_required=col.is_required,
            is_primary_key=col.is_primary_key,
            format_pattern=col.format_pattern,
            description=col.description,
            order_index=idx
        )
        db.add(c_obj)
        created_cols.append(c_obj)
    
    db.commit()

    return {
        "id": schema_obj.id,
        "organisation_id": schema_obj.organisation_id,
        "partner_id": schema_obj.partner_id,
        "schema_name": schema_obj.schema_name,
        "version": schema_obj.version,
        "status": schema_obj.status,
        "created_at": schema_obj.created_at,
        "columns": created_cols
    }

@router.post("/compare", response_model=SchemaCompareResponse)
def compare_schema_endpoint(
    req: SchemaCompareRequest,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expected_schema = db.query(Schema).filter(Schema.id == req.expected_schema_id).first()
    if not expected_schema:
        raise HTTPException(status_code=404, detail="Expected schema not found")

    expected_cols = db.query(SchemaColumn).filter(SchemaColumn.schema_id == expected_schema.id).all()
    changes = compare_schemas(expected_cols, req.incoming_columns)
    affected_deps = analyze_impact(db, current_user.organisation_id, changes)
    
    risk_assessment = RiskEngine.calculate_risk(changes, affected_deps)

    change_responses = []
    for c in changes:
        change_responses.append({
            "id": getattr(c, "id", None),
            "change_type": c.change_type,
            "column_name": c.column_name,
            "old_value": c.old_value,
            "new_value": c.new_value,
            "severity": c.severity,
            "category": c.category,
            "reason": c.reason,
            "recommendation": c.recommendation
        })

    return {
        "changes": change_responses,
        "has_breaking_changes": risk_assessment['breakdown']['breaking_changes_count'] > 0,
        "publication_decision": risk_assessment['decision'],
        "affected_dependencies": len(affected_deps)
    }
