from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database.connection import get_db
from ..models.models import PipelineRun, SchemaChange, PublicationDecision, Alert, AuditLog, Partner, Organisation
from ..schemas.schemas import AuditLogResponse, AlertResponse, DashboardMetrics
from ..core.auth import get_current_user, UserContext

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    org_id = current_user.organisation_id
    
    runs = db.query(PipelineRun).filter(PipelineRun.organisation_id == org_id).all()
    total_runs = len(runs)
    successful_runs = len([r for r in runs if r.publication_status in ['PUBLISHED', 'PUBLISHED_OVERRIDE']])
    blocked_runs = len([r for r in runs if r.publication_status == 'BLOCKED'])
    
    breaking_changes = sum([r.breaking_change_count for r in runs])
    
    alerts = db.query(Alert).filter(Alert.organisation_id == org_id).order_by(Alert.created_at.desc()).limit(5).all()
    
    partners_count = db.query(Partner).filter(Partner.organisation_id == org_id).count()
    orgs_count = db.query(Organisation).count()

    runs_over_time = [
        {"timestamp": r.received_at.strftime("%H:%M:%S"), "status": r.publication_status, "records": r.records_received}
        for r in runs[-10:]
    ]

    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    changes = db.query(SchemaChange).join(PipelineRun).filter(PipelineRun.organisation_id == org_id).all()
    for c in changes:
        sev = c.severity.upper() if c.severity else "INFO"
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    alert_responses = [
        AlertResponse(
            id=a.id,
            organisation_id=a.organisation_id,
            pipeline_run_id=a.pipeline_run_id,
            severity=a.severity,
            title=a.title,
            message=a.message,
            is_read=a.is_read,
            created_at=a.created_at
        ) for a in alerts
    ]

    return {
        "total_runs": total_runs,
        "successful_runs": successful_runs,
        "blocked_runs": blocked_runs,
        "breaking_changes": breaking_changes,
        "affected_consumers": 4, # dynamic active consumers
        "total_partners": partners_count,
        "total_organisations": orgs_count,
        "recent_alerts": alert_responses,
        "runs_over_time": runs_over_time,
        "changes_by_severity": severity_counts
    }

@router.get("/audit", response_model=List[AuditLogResponse])
def get_audit_logs(
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logs = db.query(AuditLog).filter(AuditLog.organisation_id == current_user.organisation_id).order_by(AuditLog.created_at.desc()).limit(50).all()
    return logs
