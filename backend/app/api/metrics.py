from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models import SchemaVersion, DataContract, PipelineRun, DownstreamDependency, SchemaChangeEvent, PublicationDecision, DataSource, User

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("/")
def get_metrics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    org_id = current_user.organization_id
    
    total_schemas = db.query(SchemaVersion).join(DataSource).filter(DataSource.organization_id == org_id).count()
    total_contracts = db.query(DataContract).join(DataSource).filter(DataSource.organization_id == org_id).count()
    total_pipeline_runs = db.query(PipelineRun).join(DataSource).filter(DataSource.organization_id == org_id).count()
    total_dependencies = db.query(DownstreamDependency).filter(DownstreamDependency.organization_id == org_id).count()
    total_changes = db.query(SchemaChangeEvent).join(SchemaVersion).join(DataSource).filter(DataSource.organization_id == org_id).count()
    
    blocked = db.query(PublicationDecision).join(SchemaVersion).join(DataSource).filter(
        DataSource.organization_id == org_id, PublicationDecision.decision == "BLOCK"
    ).count()
    allowed = db.query(PublicationDecision).join(SchemaVersion).join(DataSource).filter(
        DataSource.organization_id == org_id, PublicationDecision.decision == "ALLOW"
    ).count()
    overrides = db.query(PublicationDecision).join(SchemaVersion).join(DataSource).filter(
        DataSource.organization_id == org_id, PublicationDecision.decision == "OVERRIDE"
    ).count()
    
    return {
        "total_schemas": total_schemas,
        "total_contracts": total_contracts,
        "total_pipeline_runs": total_pipeline_runs,
        "total_dependencies": total_dependencies,
        "total_changes": total_changes,
        "blocked_publications": blocked,
        "allowed_publications": allowed,
        "override_publications": overrides
    }
