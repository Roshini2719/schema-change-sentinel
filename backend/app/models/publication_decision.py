from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, func
from sqlalchemy.orm import relationship
from app.database import Base


class PublicationDecision(Base):
    __tablename__ = "publication_decisions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False, index=True)
    schema_version_id = Column(Integer, ForeignKey("schema_versions.id"), nullable=True, index=True)
    decision = Column(String(50), nullable=False)
    risk_score = Column(Float, nullable=False, default=0.0)
    reason = Column(Text, nullable=True)
    decided_by = Column(String(255), nullable=True)
    override_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="publication_decisions")
    data_source = relationship("DataSource", back_populates="publication_decisions")
    schema_version = relationship("SchemaVersion", back_populates="publication_decisions")
