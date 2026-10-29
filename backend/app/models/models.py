from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text, ForeignKey, Integer, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
from ..core.config import settings

Base = declarative_base()
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_id():
    return str(uuid.uuid4())

# ─── Tenant / Auth ───────────────────────────────────────────────────────────

class Organisation(Base):
    __tablename__ = "organisations"
    id = Column(String, primary_key=True, default=generate_id)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    users = relationship("User", back_populates="organisation")
    partners = relationship("Partner", back_populates="organisation")
    schemas = relationship("DataSchema", back_populates="organisation")
    contracts = relationship("DataContract", back_populates="organisation")

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_id)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # ADMIN | DATA_ENGINEER | ANALYST | PARTNER
    organisation_id = Column(String, ForeignKey("organisations.id"), nullable=False)
    partner_id = Column(String, ForeignKey("partners.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    organisation = relationship("Organisation", back_populates="users")
    partner = relationship("Partner", back_populates="users")

class Partner(Base):
    __tablename__ = "partners"
    id = Column(String, primary_key=True, default=generate_id)
    name = Column(String, nullable=False)
    organisation_id = Column(String, ForeignKey("organisations.id"), nullable=False)
    contact_email = Column(String, nullable=True)
    status = Column(String, default="ACTIVE")  # ACTIVE | SUSPENDED | PENDING
    created_at = Column(DateTime, default=datetime.utcnow)

    organisation = relationship("Organisation", back_populates="partners")
    users = relationship("User", back_populates="partner")
    schemas = relationship("DataSchema", back_populates="partner")
    contracts = relationship("DataContract", back_populates="partner")

# ─── Schema Registry ─────────────────────────────────────────────────────────

class DataSchema(Base):
    __tablename__ = "data_schemas"
    id = Column(String, primary_key=True, default=generate_id)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False, default="1.0.0")
    partner_id = Column(String, ForeignKey("partners.id"), nullable=False)
    organisation_id = Column(String, ForeignKey("organisations.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)

    partner = relationship("Partner", back_populates="schemas")
    organisation = relationship("Organisation", back_populates="schemas")
    columns = relationship("SchemaColumn", back_populates="schema", cascade="all, delete-orphan")
    contracts = relationship("DataContract", back_populates="registered_schema")

class SchemaColumn(Base):
    __tablename__ = "schema_columns"
    id = Column(String, primary_key=True, default=generate_id)
    schema_id = Column(String, ForeignKey("data_schemas.id"), nullable=False)
    column_name = Column(String, nullable=False)
    data_type = Column(String, nullable=False)   # string | integer | decimal | boolean | datetime | date
    is_nullable = Column(Boolean, default=False)
    is_required = Column(Boolean, default=True)
    is_primary_key = Column(Boolean, default=False)
    format_pattern = Column(String, nullable=True)  # e.g., "YYYY-MM-DD"
    description = Column(Text, nullable=True)

    schema = relationship("DataSchema", back_populates="columns")

# ─── Data Contract ────────────────────────────────────────────────────────────

class DataContract(Base):
    __tablename__ = "data_contracts"
    id = Column(String, primary_key=True, default=generate_id)
    name = Column(String, nullable=False)
    partner_id = Column(String, ForeignKey("partners.id"), nullable=False)
    organisation_id = Column(String, ForeignKey("organisations.id"), nullable=False)
    registered_schema_id = Column(String, ForeignKey("data_schemas.id"), nullable=False)
    sla_hours = Column(Integer, default=24)
    status = Column(String, default="ACTIVE")   # ACTIVE | SUSPENDED | EXPIRED
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    partner = relationship("Partner", back_populates="contracts")
    organisation = relationship("Organisation", back_populates="contracts")
    registered_schema = relationship("DataSchema", back_populates="contracts")

# ─── Downstream Dependencies ──────────────────────────────────────────────────

class DownstreamDependency(Base):
    __tablename__ = "downstream_dependencies"
    id = Column(String, primary_key=True, default=generate_id)
    schema_id = Column(String, ForeignKey("data_schemas.id"), nullable=False)
    organisation_id = Column(String, ForeignKey("organisations.id"), nullable=False)
    consumer_name = Column(String, nullable=False)
    consumer_type = Column(String, nullable=False)  # REPORT | DASHBOARD | API | ML_MODEL | ETL
    query_snippet = Column(Text, nullable=True)
    columns_used = Column(JSON, nullable=True)       # list of column names depended on
    criticality = Column(String, default="HIGH")     # CRITICAL | HIGH | MEDIUM | LOW
    owner_email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ─── Pipeline Runs ────────────────────────────────────────────────────────────

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"
    id = Column(String, primary_key=True, default=generate_id)
    partner_id = Column(String, ForeignKey("partners.id"), nullable=False)
    organisation_id = Column(String, ForeignKey("organisations.id"), nullable=False)
    schema_id = Column(String, ForeignKey("data_schemas.id"), nullable=True)
    run_timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)          # PUBLISHED | BLOCKED | ERROR | PENDING
    gate_decision = Column(String, nullable=True)    # ALLOW | BLOCK | ERROR
    breaking_changes_count = Column(Integer, default=0)
    warning_changes_count = Column(Integer, default=0)
    incoming_schema_snapshot = Column(JSON, nullable=True)
    changes_detected = Column(JSON, nullable=True)
    affected_consumers = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    triggered_by = Column(String, nullable=True)

# ─── Audit Log ────────────────────────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=generate_id)
    organisation_id = Column(String, nullable=False)
    user_id = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=True)
    resource_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)