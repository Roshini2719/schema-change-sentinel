"""
Validate router — the publication gate.
POST /api/validate  →  runs sentinel engine, records pipeline run, returns gate decision.
"""
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ..models.models import get_db, DataSchema, DownstreamDependency, PipelineRun, Partner, DataContract
from ..core.auth import get_current_user, UserContext
from ..schemas.schemas import ValidateRequest, GateDecisionResponse, SchemaChangeEventResponse, PipelineRunResponse
from ..services.schema_sentinel import run_sentinel
from ..services.audit_service import log_action
from dataclasses import asdict

router = APIRouter(prefix="/api", tags=["validation"])

def _change_to_response(c) -> SchemaChangeEventResponse:
    return SchemaChangeEventResponse(
        change_type=c.change_type,
        column_name=c.column_name,
        old_value=c.old_value,
        new_value=c.new_value,
        severity=c.severity,
        category=c.category,
        reason=c.reason,
        recommendation=c.recommendation,
        affected_consumers=c.affected_consumers,
    )

@router.post("/validate", response_model=GateDecisionResponse)
def validate_schema(
    body: ValidateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    t0 = time.time()

    # 1. Fetch registered schema (tenant-scoped)
    schema = db.query(DataSchema).filter(
        DataSchema.id == body.schema_id,
        DataSchema.organisation_id == current_user.organisation_id,
    ).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found in your organisation")

    # 2. PARTNER role: may only validate their own partner's schema
    if current_user.role == "PARTNER":
        if schema.partner_id != current_user.partner_id:
            raise HTTPException(status_code=403, detail="Partners can only validate their own schema")

    # 3. Fetch downstream dependencies
    dependencies = db.query(DownstreamDependency).filter(
        DownstreamDependency.schema_id == schema.id
    ).all()

    # 4. Run sentinel (fail-closed)
    incoming = [col.model_dump() for col in body.incoming_columns]
    decision = run_sentinel(schema.columns, incoming, dependencies)

    elapsed_ms = round((time.time() - t0) * 1000, 2)

    # 5. Persist pipeline run
    pipeline_run = PipelineRun(
        partner_id=schema.partner_id,
        organisation_id=current_user.organisation_id,
        schema_id=schema.id,
        status="BLOCKED" if decision.decision == "BLOCK" else "PUBLISHED",
        gate_decision=decision.decision,
        breaking_changes_count=len(decision.breaking_changes),
        warning_changes_count=len(decision.warning_changes),
        incoming_schema_snapshot=incoming,
        changes_detected=[
            {
                "change_type": c.change_type,
                "column_name": c.column_name,
                "old_value": c.old_value,
                "new_value": c.new_value,
                "severity": c.severity,
                "category": c.category,
                "reason": c.reason,
            }
            for c in decision.all_changes
        ],
        affected_consumers=decision.affected_consumers,
        error_message=decision.reason if decision.decision == "BLOCK" and decision.is_fail_closed else None,
        triggered_by=current_user.email,
    )
    db.add(pipeline_run)
    db.commit()
    db.refresh(pipeline_run)

    # 6. Audit
    log_action(
        db=db,
        organisation_id=current_user.organisation_id,
        user_id=current_user.user_id,
        user_email=current_user.email,
        action=f"GATE_{decision.decision}",
        resource_type="pipeline_run",
        resource_id=pipeline_run.id,
        details={
            "schema_id": schema.id,
            "schema_name": schema.name,
            "decision": decision.decision,
            "breaking_changes": len(decision.breaking_changes),
            "warning_changes": len(decision.warning_changes),
            "affected_consumers": decision.affected_consumers,
            "latency_ms": elapsed_ms,
            "is_fail_closed": decision.is_fail_closed,
            "run_label": body.run_label,
        },
        ip_address=request.client.host if request.client else None,
    )

    return GateDecisionResponse(
        decision=decision.decision,
        reason=decision.reason,
        pipeline_run_id=pipeline_run.id,
        breaking_changes=[_change_to_response(c) for c in decision.breaking_changes],
        warning_changes=[_change_to_response(c) for c in decision.warning_changes],
        info_changes=[_change_to_response(c) for c in decision.info_changes],
        affected_consumers=decision.affected_consumers,
        is_fail_closed=decision.is_fail_closed,
    )

@router.get("/pipeline-runs", response_model=List[PipelineRunResponse])
def list_pipeline_runs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    q = db.query(PipelineRun).filter(
        PipelineRun.organisation_id == current_user.organisation_id
    )
    if current_user.role == "PARTNER" and current_user.partner_id:
        q = q.filter(PipelineRun.partner_id == current_user.partner_id)
    return q.order_by(PipelineRun.run_timestamp.desc()).limit(limit).all()

@router.get("/pipeline-runs/{run_id}", response_model=PipelineRunResponse)
def get_pipeline_run(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    run = db.query(PipelineRun).filter(
        PipelineRun.id == run_id,
        PipelineRun.organisation_id == current_user.organisation_id,
    ).first()
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    return run
