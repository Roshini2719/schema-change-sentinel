from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from typing import Optional
import json


def log_audit_event(
    db: Session,
    organization_id: int,
    user_id: Optional[int],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[dict] = None,
) -> AuditLog:
    log_entry = AuditLog(
        organization_id=organization_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=json.dumps(details) if details else None,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
