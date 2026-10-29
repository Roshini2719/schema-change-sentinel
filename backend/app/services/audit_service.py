"""
Audit Service — records every action taken by the system or a user.
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..models.models import AuditLog

logger = logging.getLogger(__name__)

def log_action(
    db: Session,
    organisation_id: str,
    action: str,
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """
    Persist an audit log entry.
    If the DB write itself fails, we log to stderr but do NOT re-raise
    so that the gate decision is still returned to the caller.
    """
    entry = AuditLog(
        organisation_id=organisation_id,
        user_id=user_id,
        user_email=user_email,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
    )
    try:
        db.add(entry)
        db.commit()
        db.refresh(entry)
    except Exception as exc:
        logger.error("AUDIT WRITE FAILED (action=%s, org=%s): %s", action, organisation_id, exc)
        db.rollback()
        # Still return the (unsaved) entry so callers can inspect it
    return entry