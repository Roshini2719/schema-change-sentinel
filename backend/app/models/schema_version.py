from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.database import Base


class SchemaVersion(Base):
    __tablename__ = "schema_versions"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    schema_json = Column(Text, nullable=False)
    schema_hash = Column(String(64), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)

    data_source = relationship("DataSource", back_populates="schema_versions")
    fields = relationship("SchemaField", back_populates="schema_version", cascade="all, delete-orphan")
    pipeline_runs = relationship("PipelineRun", back_populates="schema_version")
    old_change_events = relationship("SchemaChangeEvent", foreign_keys="SchemaChangeEvent.old_schema_version_id", back_populates="old_schema_version")
    new_change_events = relationship("SchemaChangeEvent", foreign_keys="SchemaChangeEvent.new_schema_version_id", back_populates="new_schema_version")
    publication_decisions = relationship("PublicationDecision", back_populates="schema_version")
