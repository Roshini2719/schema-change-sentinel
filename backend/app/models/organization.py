from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    status = Column(String(50), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="organization")
    partners = relationship("Partner", back_populates="organization")
    data_sources = relationship("DataSource", back_populates="organization")
    data_contracts = relationship("DataContract", back_populates="organization")
    pipeline_runs = relationship("PipelineRun", back_populates="organization")
    downstream_dependencies = relationship("DownstreamDependency", back_populates="organization")
    schema_change_events = relationship("SchemaChangeEvent", back_populates="organization")
    publication_decisions = relationship("PublicationDecision", back_populates="organization")
    audit_logs = relationship("AuditLog", back_populates="organization")
    notifications = relationship("Notification", back_populates="organization")
