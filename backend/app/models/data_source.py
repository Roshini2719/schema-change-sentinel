from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.database import Base


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(100), nullable=False, default="transaction")
    description = Column(Text, nullable=True)
    current_schema_version = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="data_sources")
    partner = relationship("Partner", back_populates="data_sources")
    schema_versions = relationship("SchemaVersion", back_populates="data_source")
    data_contracts = relationship("DataContract", back_populates="data_source")
    pipeline_runs = relationship("PipelineRun", back_populates="data_source")
    schema_change_events = relationship("SchemaChangeEvent", back_populates="data_source")
    publication_decisions = relationship("PublicationDecision", back_populates="data_source")
