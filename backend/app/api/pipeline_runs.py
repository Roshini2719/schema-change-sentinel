from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models import PipelineRun, DataSource, User
from app.schemas.pipeline import PipelineRunCreate, PipelineRunResponse
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/api/pipeline-runs", tags=["pipeline_runs"])

@router.get("/", response_model=List[PipelineRunResponse])
def list_pipeline_runs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(PipelineRun).join(DataSource).filter(DataSource.organization_id == current_user.organization_id).all()

@router.post("/", response_model=PipelineRunResponse)
def create_pipeline_run(
    run: PipelineRunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DATA_ENGINEER"]))
):
    data_source = db.query(DataSource).filter(
        DataSource.id == run.data_source_id,
        DataSource.organization_id == current_user.organization_id
    ).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    db_run = PipelineRun(**run.dict())
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    log_audit_event(db, current_user.id, current_user.organization_id, "CREATE_PIPELINE_RUN", f"Created pipeline run for DS {db_run.data_source_id}")
    return db_run
