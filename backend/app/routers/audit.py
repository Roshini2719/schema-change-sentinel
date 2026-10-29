from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..models.models import get_db, AuditLog
from ..core.auth import get_current_user, UserContext
from ..schemas.schemas import AuditLogResponse

router = APIRouter(prefix="/api/audit", tags=["audit"])

@router.get("", response_model=List[AuditLogResponse])
def list_audit_logs(
    limit: int = Query(100, le=500),
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Retrieve audit logs for the current organisation."""
    q = db.query(AuditLog).filter(
        AuditLog.organisation_id == current_user.organisation_id
    )
    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action}%"))
    # PARTNER role: only their own entries
    if current_user.role == "PARTNER":
        q = q.filter(AuditLog.user_id == current_user.user_id)
    return q.order_by(AuditLog.timestamp.desc()).limit(limit).all()
