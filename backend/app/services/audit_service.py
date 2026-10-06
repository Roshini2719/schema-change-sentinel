from ..models.models import AuditLog

def log_action(db, organisation_id, user_id, user_email, action, resource_type=None, resource_id=None, details=None):
    audit_log = AuditLog(
        organisation_id=organisation_id,
        user_id=user_id,
        user_email=user_email,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log