from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Float, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
from ..core.config import settings

from ..database.connection import engine, SessionLocal, Base, get_db

def generate_id():
    return str(uuid.uuid4())

import enum

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    DATA_ENGINEER = "DATA_ENGINEER"
    DATA_ANALYST = "ANALYST"
    ANALYST = "ANALYST"
    PARTNER = "PARTNER"

# ─── Tenant / Auth ───────────────────────────────────────────────────────────

class Organisation(Base):
    __tablename__ = "organisations"
    id = Column(String, primary_key=True, default=generate_id)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def __init__(self, **kwargs):
        if "status" in kwargs and "is_active" not in kwargs:
            kwargs["is_active"] = (kwargs.pop("status") == "active")
        super().__init__(**kwargs)

    @property
    def status(self):
        return "active" if self.is_active else "inactive"

    @status.setter
    def status(self, val):
        self.is_active = (val == "active")

    users = relationship("User", back_populates="organisation")
    partners = relationship("Partner", back_populates="organisation")
    schemas = relationship("DataSchema", back_populates="organisation")
    contracts = relationship("DataContract", back_populates="organisation")

Organization = Organisation

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_id)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    _role = Column("role", String, nullable=False)  # ADMIN | DATA_ENGINEER | ANALYST | PARTNER
    organisation_id = Column(String, ForeignKey("organisations.id"), nullable=False)
    partner_id = Column(String, ForeignKey("partners.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def __init__(self, **kwargs):
        if "organization_id" in kwargs and "organisation_id" not in kwargs:
            kwargs["organisation_id"] = kwargs.pop("organization_id")
        if "name" in kwargs and "full_name" not in kwargs:
            kwargs["full_name"] = kwargs.pop("name")
        if "password_hash" in kwargs and "hashed_password" not in kwargs:
            kwargs["hashed_password"] = kwargs.pop("password_hash")
        if "status" in kwargs and "is_active" not in kwargs:
            kwargs["is_active"] = (kwargs.pop("status") == "active")
        if "role" in kwargs:
            r = kwargs.pop("role")
            kwargs["_role"] = r.value if hasattr(r, "value") else str(r)
        super().__init__(**kwargs)

    @property
    def role(self):
        try:
            return UserRole(self._role)
        except Exception:
            return self._role

    @role.setter
    def role(self, val):
        self._role = val.value if hasattr(val, "value") else str(val)

    @property
    def organization_id(self):
        return self.organisation_id

    @organization_id.setter
    def organization_id(self, val):
        self.organisation_id = val

    @property
    def name(self):
        return self.full_name

    @name.setter
    def name(self, val):
        self.full_name = val

    @property
    def password_hash(self):
        return self.hashed_password

    @password_hash.setter
    def password_hash(self, val):
        self.hashed_password = val

    @property
    def status(self):
        return "active" if self.is_active else "inactive"

    @status.setter
    def status(self, val):
        self.is_active = (val == "active")

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

    def __init__(self, **kwargs):
        if "organization_id" in kwargs and "organisation_id" not in kwargs:
            kwargs["organisation_id"] = kwargs.pop("organization_id")
        super().__init__(**kwargs)

    @property
    def organization_id(self):
        return self.organisation_id

    @organization_id.setter
    def organization_id(self, val):
        self.organisation_id = val

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
    name = Column(String, nullable=True)
    contract_name = Column(String, nullable=True)
    partner_id = Column(String, ForeignKey("partners.id"), nullable=False)
    organisation_id = Column(String, ForeignKey("organisations.id"), nullable=False)
    registered_schema_id = Column(String, ForeignKey("data_schemas.id"), nullable=True)
    version = Column(Integer, default=1)
    sla_hours = Column(Integer, default=24)
    status = Column(String, default="ACTIVE")   # ACTIVE | SUSPENDED | EXPIRED
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    created_by = Column(String, nullable=True)

    partner = relationship("Partner", back_populates="contracts")
    organisation = relationship("Organisation", back_populates="contracts")
    registered_schema = relationship("DataSchema", back_populates="contracts")

class ContractRule(Base):
    __tablename__ = "contract_rules"
    id = Column(String, primary_key=True, default=generate_id)
    contract_id = Column(String, ForeignKey("data_contracts.id"), nullable=False)
    column_name = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    is_required = Column(Boolean, default=True)
    is_nullable = Column(Boolean, default=False)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    allowed_values = Column(String, nullable=True)
    regex_pattern = Column(String, nullable=True)
    description = Column(String, nullable=True)

# ─── Downstream Dependencies ──────────────────────────────────────────────────

class DownstreamDependency(Base):
    __tablename__ = "downstream_dependencies"
    id = Column(String, primary_key=True, default=generate_id)
    schema_id = Column(String, ForeignKey("data_schemas.id"), nullable=True)
    organisation_id = Column(String, ForeignKey("organisations.id"), nullable=False)
    consumer_name = Column(String, nullable=True)
    name = Column(String, nullable=True)
    consumer_type = Column(String, nullable=True)  # REPORT | DASHBOARD | API | ML_MODEL | ETL
    query_snippet = Column(Text, nullable=True)
    columns_used = Column(JSON, nullable=True)       # list of column names depended on
    criticality = Column(String, default="HIGH")     # CRITICAL | HIGH | MEDIUM | LOW
    owner_email = Column(String, nullable=True)
    owner = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DependencyColumn(Base):
    __tablename__ = "dependency_columns"
    id = Column(String, primary_key=True, default=generate_id)
    dependency_id = Column(String, ForeignKey("downstream_dependencies.id"), nullable=False)
    column_name = Column(String, nullable=False)
    is_critical = Column(Boolean, default=True)

# ─── Pipeline Runs ────────────────────────────────────────────────────────────

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"
    id = Column(String, primary_key=True, default=generate_id)
    partner_id = Column(String, ForeignKey("partners.id"), nullable=False)
    organisation_id = Column(String, ForeignKey("organisations.id"), nullable=False)
    schema_id = Column(String, ForeignKey("data_schemas.id"), nullable=True)
    schema_version = Column(Integer, default=1)
    run_timestamp = Column(DateTime, default=datetime.utcnow)
    received_at = Column(DateTime, default=datetime.utcnow)
    validation_started_at = Column(DateTime, nullable=True)
    validation_completed_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="RECEIVED")          # PUBLISHED | BLOCKED | ERROR | PENDING
    publication_status = Column(String, default="PENDING")
    gate_decision = Column(String, nullable=True)    # ALLOW | BLOCK | ERROR
    breaking_changes_count = Column(Integer, default=0)
    breaking_change_count = Column(Integer, default=0)
    warning_changes_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    schema_change_count = Column(Integer, default=0)
    records_received = Column(Integer, default=0)
    records_valid = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)
    incoming_schema_snapshot = Column(JSON, nullable=True)
    changes_detected = Column(JSON, nullable=True)
    affected_consumers = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    failure_reason = Column(String, nullable=True)
    triggered_by = Column(String, nullable=True)
    is_baseline = Column(Boolean, default=False)

# ─── Schema Changes & Publication Decisions ──────────────────────────────────

class SchemaChange(Base):
    __tablename__ = "schema_changes"
    id = Column(String, primary_key=True, default=generate_id)
    pipeline_run_id = Column(String, ForeignKey("pipeline_runs.id"), nullable=True)
    change_type = Column(String, nullable=False)
    column_name = Column(String, nullable=False)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    severity = Column(String, nullable=False)
    category = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    recommendation = Column(String, nullable=True)

class PublicationDecision(Base):
    __tablename__ = "publication_decisions"
    id = Column(String, primary_key=True, default=generate_id)
    pipeline_run_id = Column(String, ForeignKey("pipeline_runs.id"), nullable=True)
    decision = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    decided_at = Column(DateTime, default=datetime.utcnow)
    decided_by = Column(String, nullable=True)
    breaking_changes = Column(Integer, default=0)
    affected_dependencies = Column(Integer, default=0)
    override_justification = Column(String, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True, default=generate_id)
    organisation_id = Column(String, ForeignKey("organisations.id"), nullable=False)
    pipeline_run_id = Column(String, ForeignKey("pipeline_runs.id"), nullable=True)
    severity = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

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
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(String, primary_key=True, default=generate_id)
    organisation_id = Column(String, ForeignKey("organisations.id"), nullable=True)
    respondent_role = Column(String, nullable=False)
    clarity_score = Column(Integer, nullable=False)
    usefulness_score = Column(Integer, nullable=False)
    schema_diff_clarity = Column(Integer, nullable=False)
    dashboard_helpfulness = Column(Integer, nullable=False)
    risk_reduction_confidence = Column(Integer, nullable=False)
    suggestions = Column(String, nullable=True)
    is_simulated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Aliases for compatibility
Schema = DataSchema
DataSource = Partner
SchemaVersion = DataSchema
SchemaField = SchemaColumn
SchemaChangeEvent = SchemaChange
Notification = Alert
ValidationFeedback = Feedback