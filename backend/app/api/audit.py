from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models import AuditLog, User

router = APIRouter(prefix="/api/audit-logs", tags=["audit"])

@router.get("/")
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DATA_ENGINEER"]))
):
    return db.query(AuditLog).filter(AuditLog.organization_id == current_user.organization_id).all()
