from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models import SchemaChangeEvent, SchemaVersion, DataSource, User

router = APIRouter(prefix="/api/schema-changes", tags=["schema_changes"])

@router.get("/")
def list_changes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(SchemaChangeEvent).join(SchemaVersion).join(DataSource).filter(
        DataSource.organization_id == current_user.organization_id
    ).all()

@router.get("/{change_id}")
def get_change(change_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    change = db.query(SchemaChangeEvent).join(SchemaVersion).join(DataSource).filter(
        SchemaChangeEvent.id == change_id,
        DataSource.organization_id == current_user.organization_id
    ).first()
    if not change:
        raise HTTPException(status_code=404, detail="Change not found")
    return change
