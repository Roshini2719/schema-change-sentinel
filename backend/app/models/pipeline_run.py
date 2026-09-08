from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.database import Base


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False, index=True)
    schema_version_id = Column(Integer, ForeignKey("schema_versions.id"), nullable=True, index=True)
    run_id = Column(String(255), nullable=False, unique=True)
    status = Column(String(50), nullable=False, default="running")
    expected_records = Column(Integer, nullable=True)
    records_received = Column(Integer, nullable=True, default=0)
    records_processed = Column(Integer, nullable=True, default=0)
    records_rejected = Column(Integer, nullable=True, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    organization = relationship("Organization", back_populates="pipeline_runs")
    data_source = relationship("DataSource", back_populates="pipeline_runs")
    schema_version = relationship("SchemaVersion", back_populates="pipeline_runs")
