from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database.connection import get_db
from ..models.models import PipelineRun, Schema, SchemaColumn, SchemaChange, PublicationDecision, Alert
from ..schemas.schemas import PipelineRunCreate, PipelineRunResponse, PublicationOverrideRequest
from ..core.auth import get_current_user, UserContext, role_required, Roles
from ..services.schema_sentinel import compare_schemas
from ..services.dependency_analyzer import analyze_impact
from ..services.risk_engine import RiskEngine
from ..services.audit_service import log_action

router = APIRouter(prefix="/api/validation", tags=["validation"])

@router.post("/run", response_model=PipelineRunResponse)
def run_validation(
    req: PipelineRunCreate,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    run = PipelineRun(
        organisation_id=current_user.organisation_id,
        partner_id=req.partner_id,
        schema_version=req.schema_version,
        records_received=req.records_received,
        status="RUNNING",
        validation_started_at=datetime.utcnow()
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Get active registered schema for partner
    registered_schema = db.query(Schema).filter(
        Schema.partner_id == req.partner_id,
        Schema.version == req.schema_version,
        Schema.status == 'ACTIVE'
    ).first()

    if not registered_schema:
        # Fallback to latest registered schema if version match fails
        registered_schema = db.query(Schema).filter(
            Schema.partner_id == req.partner_id,
            Schema.status == 'ACTIVE'
        ).order_by(Schema.version.desc()).first()

    if not registered_schema:
        run.status = "FAILED"
        run.publication_status = "BLOCKED"
        run.failure_reason = "No active registered schema contract found for partner."
        run.validation_completed_at = datetime.utcnow()
        db.commit()
        return run

    expected_cols = db.query(SchemaColumn).filter(SchemaColumn.schema_id == registered_schema.id).all()
    changes = compare_schemas(expected_cols, req.incoming_columns)
    affected_deps = analyze_impact(db, current_user.organisation_id, changes)
    
    risk_res = RiskEngine.calculate_risk(changes, affected_deps)

    for c in changes:
        sc = SchemaChange(
            pipeline_run_id=run.id,
            change_type=c.change_type,
            column_name=c.column_name,
            old_value=c.old_value,
            new_value=c.new_value,
            severity=c.severity,
            category=c.category,
            reason=c.reason,
            recommendation=c.recommendation
        )
        db.add(sc)

    pub_dec = PublicationDecision(
        pipeline_run_id=run.id,
        decision=risk_res['decision'],
        reason=risk_res['reason'],
        breaking_changes=risk_res['breakdown']['breaking_changes_count'],
        affected_dependencies=risk_res['breakdown']['affected_dependencies_count']
    )
    db.add(pub_dec)

    run.status = "COMPLETED"
    run.validation_completed_at = datetime.utcnow()
    run.schema_change_count = len(changes)
    run.breaking_change_count = risk_res['breakdown']['breaking_changes_count']
    run.publication_status = "PUBLISHED" if risk_res['decision'] == 'ALLOW' else "BLOCKED"
    
    if risk_res['decision'] == 'BLOCK':
        run.failure_reason = risk_res['reason']
        # Raise Alert
        alert = Alert(
            organisation_id=current_user.organisation_id,
            pipeline_run_id=run.id,
            severity="HIGH",
            title=f"Publication Blocked for Partner Run #{run.id[:8]}",
            message=risk_res['reason']
        )
        db.add(alert)

    db.commit()
    db.refresh(run)

    log_action(
        db, current_user.organisation_id, current_user.user_id, current_user.email,
        action="PIPELINE_VALIDATION", resource_type="pipeline_run", resource_id=run.id,
        details=f"Decision: {risk_res['decision']}, Risk Score: {risk_res['risk_score']}"
    )

    return run

@router.post("/override")
def override_publication(
    req: PublicationOverrideRequest,
    current_user: UserContext = Depends(role_required([Roles.ADMIN, Roles.DATA_ENGINEER])),
    db: Session = Depends(get_db)
):
    run = db.query(PipelineRun).filter(PipelineRun.id == req.pipeline_run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")

    decision = db.query(PublicationDecision).filter(PublicationDecision.pipeline_run_id == run.id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Publication decision record not found")

    decision.decision = "OVERRIDE"
    decision.decided_by = current_user.user_id
    decision.override_justification = req.justification

    run.publication_status = "PUBLISHED_OVERRIDE"
    db.commit()

    log_action(
        db, current_user.organisation_id, current_user.user_id, current_user.email,
        action="PUBLICATION_OVERRIDE", resource_type="pipeline_run", resource_id=run.id,
        details=f"Justification: {req.justification}"
    )

    return {"status": "SUCCESS", "message": f"Run {run.id} publication overridden successfully."}
