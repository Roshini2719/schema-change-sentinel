from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles, require_admin
from app.models import DataSource, SchemaVersion, DataContract, DownstreamDependency, PipelineRun, SchemaChangeEvent, PublicationDecision, Notification, User
from app.schemas.publication import PublicationCheckRequest, PublicationCheckResponse, PublicationApproveRequest, PublicationOverrideRequest
from app.services.publication_gate import evaluate_publication
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/api/publication", tags=["publication"])

@router.post("/check", response_model=PublicationCheckResponse)
def check_publication(
    req: PublicationCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DATA_ENGINEER", "PARTNER"]))
):
    data_source = db.query(DataSource).filter(
        DataSource.id == req.data_source_id,
        DataSource.organization_id == current_user.organization_id
    ).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
        
    schema_version = db.query(SchemaVersion).filter(SchemaVersion.id == req.schema_version_id).first()
    if not schema_version or schema_version.data_source_id != data_source.id:
        raise HTTPException(status_code=404, detail="Schema version not found for this data source")

    current_schema = db.query(SchemaVersion).filter(SchemaVersion.id == data_source.current_schema_version_id).first()
    contract = db.query(DataContract).filter(DataContract.data_source_id == data_source.id, DataContract.is_active == True).first()
    dependencies = db.query(DownstreamDependency).filter(DownstreamDependency.data_source_id == data_source.id).all()
    recent_runs = db.query(PipelineRun).filter(PipelineRun.data_source_id == data_source.id).order_by(PipelineRun.run_timestamp.desc()).limit(10).all()

    result = evaluate_publication(
        new_schema=schema_version.schema_json,
        old_schema=current_schema.schema_json if current_schema else None,
        contract=contract,
        dependencies=dependencies,
        pipeline_runs=recent_runs
    )

    for change in result.get("changes", []):
        evt = SchemaChangeEvent(
            schema_version_id=schema_version.id,
            change_type=change.get("type"),
            field_name=change.get("field"),
            is_breaking=change.get("breaking", False),
            severity=change.get("severity", "LOW")
        )
        db.add(evt)
    
    decision = PublicationDecision(
        schema_version_id=schema_version.id,
        decision="BLOCK" if result.get("is_blocked") else "ALLOW",
        reason=result.get("reason"),
        risk_score=result.get("risk_score")
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)
    
    if decision.decision == "BLOCK":
        notif = Notification(
            organization_id=current_user.organization_id,
            message=f"Publication blocked for DS {data_source.id} due to breaking changes.",
            is_read=False
        )
        db.add(notif)
        db.commit()

    log_audit_event(db, current_user.id, current_user.organization_id, "PUBLICATION_CHECK", f"Checked pub for schema {schema_version.id}: {decision.decision}")
    
    return {"decision": decision.decision, "reason": decision.reason, "risk_score": decision.risk_score}

@router.post("/approve")
def approve_schema(
    req: PublicationApproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DATA_ENGINEER"]))
):
    data_source = db.query(DataSource).filter(
        DataSource.id == req.data_source_id,
        DataSource.organization_id == current_user.organization_id
    ).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    schema_version = db.query(SchemaVersion).filter(SchemaVersion.id == req.schema_version_id, SchemaVersion.data_source_id == req.data_source_id).first()
    if not schema_version:
        raise HTTPException(status_code=404, detail="Schema version not found")

    schema_version.status = "approved"
    data_source.current_schema_version_id = schema_version.id
    
    decision = PublicationDecision(
        schema_version_id=schema_version.id,
        decision="APPROVED",
        reason="Manually approved"
    )
    db.add(decision)
    db.commit()
    
    log_audit_event(db, current_user.id, current_user.organization_id, "APPROVE_SCHEMA", f"Approved schema {schema_version.id}")
    return {"status": "success"}

@router.post("/override")
def override_publication(
    req: PublicationOverrideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if not req.confirmation or len(req.reason) < 10:
        raise HTTPException(status_code=400, detail="Valid reason (min 10 chars) and confirmation required")
        
    schema_version = db.query(SchemaVersion).filter(SchemaVersion.id == req.schema_version_id).first()
    if not schema_version:
        raise HTTPException(status_code=404, detail="Schema version not found")
        
    data_source = db.query(DataSource).filter(
        DataSource.id == schema_version.data_source_id,
        DataSource.organization_id == current_user.organization_id
    ).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    schema_version.status = "approved"
    data_source.current_schema_version_id = schema_version.id
    
    decision = PublicationDecision(
        schema_version_id=schema_version.id,
        decision="OVERRIDE",
        reason=req.reason
    )
    db.add(decision)
    db.commit()
    
    log_audit_event(db, current_user.id, current_user.organization_id, "OVERRIDE_PUBLICATION", f"Overrode block for schema {schema_version.id}: {req.reason}")
    return {"status": "success"}
