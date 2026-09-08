from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class SchemaField(Base):
    __tablename__ = "schema_fields"

    id = Column(Integer, primary_key=True, index=True)
    schema_version_id = Column(Integer, ForeignKey("schema_versions.id"), nullable=False, index=True)
    field_name = Column(String(255), nullable=False)
    data_type = Column(String(100), nullable=False)
    nullable = Column(Boolean, nullable=False, default=False)
    required = Column(Boolean, nullable=False, default=True)
    default_value = Column(String(255), nullable=True)
    is_primary_key = Column(Boolean, nullable=False, default=False)
    enum_values = Column(Text, nullable=True)  # JSON array as string

    schema_version = relationship("SchemaVersion", back_populates="fields")
