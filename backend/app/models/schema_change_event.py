from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.database import Base


class SchemaChangeEvent(Base):
    __tablename__ = "schema_change_events"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False, index=True)
    old_schema_version_id = Column(Integer, ForeignKey("schema_versions.id"), nullable=True)
    new_schema_version_id = Column(Integer, ForeignKey("schema_versions.id"), nullable=True)
    change_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    field_name = Column(String(255), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="schema_change_events")
    data_source = relationship("DataSource", back_populates="schema_change_events")
    old_schema_version = relationship("SchemaVersion", foreign_keys=[old_schema_version_id], back_populates="old_change_events")
    new_schema_version = relationship("SchemaVersion", foreign_keys=[new_schema_version_id], back_populates="new_change_events")
