from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models import SchemaVersion, SchemaField, DataSource, User
from app.schemas.schema import SchemaRegisterRequest, SchemaVersionResponse, SchemaCompareRequest, SchemaCompareResponse, SchemaValidateRequest
from app.services.schema_hasher import hash_schema
from app.services.schema_detector import detect_schema_changes
from app.services.contract_validator import validate_contract
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/api/schemas", tags=["schemas"])

@router.get("/", response_model=List[SchemaVersionResponse])
def list_schema_versions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(SchemaVersion).join(DataSource).filter(DataSource.organization_id == current_user.organization_id).all()

@router.post("/", response_model=SchemaVersionResponse)
def register_schema(
    req: SchemaRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data_source = db.query(DataSource).filter(
        DataSource.id == req.data_source_id,
        DataSource.organization_id == current_user.organization_id
    ).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
        
    schema_hash = hash_schema(req.schema_json)
    existing_schema = db.query(SchemaVersion).filter(
        SchemaVersion.data_source_id == req.data_source_id,
        SchemaVersion.schema_hash == schema_hash
    ).first()
    
    if existing_schema:
        return existing_schema
        
    new_schema = SchemaVersion(
        data_source_id=req.data_source_id,
        schema_json=req.schema_json,
        schema_hash=schema_hash,
        version_string=req.version_string,
        status="pending"
    )
    db.add(new_schema)
    db.commit()
    db.refresh(new_schema)
    
    fields = req.schema_json.get("fields", [])
    for field in fields:
        sf = SchemaField(
            schema_version_id=new_schema.id,
            field_name=field.get("name"),
            field_type=field.get("type"),
            is_nullable=field.get("nullable", True)
        )
        db.add(sf)
    db.commit()
    
    log_audit_event(db, current_user.id, current_user.organization_id, "REGISTER_SCHEMA", f"Registered new schema for DS {req.data_source_id}")
    return new_schema

@router.get("/{schema_id}", response_model=SchemaVersionResponse)
def get_schema(schema_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    schema = db.query(SchemaVersion).join(DataSource).filter(
        SchemaVersion.id == schema_id,
        DataSource.organization_id == current_user.organization_id
    ).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    return schema

@router.post("/compare", response_model=SchemaCompareResponse)
def compare_schema(
    req: SchemaCompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data_source = db.query(DataSource).filter(
        DataSource.id == req.data_source_id,
        DataSource.organization_id == current_user.organization_id
    ).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
        
    current_schema = db.query(SchemaVersion).filter(
        SchemaVersion.id == data_source.current_schema_version_id
    ).first()
    
    old_schema_json = current_schema.schema_json if current_schema else {}
    changes = detect_schema_changes(old_schema_json, req.new_schema)
    
    return {"changes": changes}

@router.post("/validate")
def validate_schema(
    req: SchemaValidateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data_source = db.query(DataSource).filter(
        DataSource.id == req.data_source_id,
        DataSource.organization_id == current_user.organization_id
    ).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    result = validate_contract(req.schema_json, req.contract_id, db)
    return {"is_valid": result}
