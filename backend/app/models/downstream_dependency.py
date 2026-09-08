from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.database import Base


class DownstreamDependency(Base):
    __tablename__ = "downstream_dependencies"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    dependency_type = Column(String(100), nullable=False, default="query")
    query_text = Column(Text, nullable=True)
    target_table = Column(String(255), nullable=True)
    criticality = Column(String(50), nullable=False, default="medium")
    owner = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="downstream_dependencies")
    fields = relationship("DependencyField", back_populates="dependency", cascade="all, delete-orphan")


class DependencyField(Base):
    __tablename__ = "dependency_fields"

    id = Column(Integer, primary_key=True, index=True)
    dependency_id = Column(Integer, ForeignKey("downstream_dependencies.id"), nullable=False, index=True)
    field_name = Column(String(255), nullable=False)

    dependency = relationship("DownstreamDependency", back_populates="fields")
