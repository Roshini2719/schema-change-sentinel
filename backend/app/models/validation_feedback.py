from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from app.database import Base


class ValidationFeedback(Base):
    __tablename__ = "validation_feedback"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    schema_version_id = Column(Integer, ForeignKey("schema_versions.id"), nullable=True)
    feedback_type = Column(String(100), nullable=False)
    message = Column(Text, nullable=True)
    submitted_by = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
