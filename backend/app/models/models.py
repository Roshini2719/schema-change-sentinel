from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from datetime import datetime
from uuid import uuid4
from ..database.connection import Base

class Organisation(Base):
    __tablename__ = 'organisations'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    organisation_id = Column(String, ForeignKey('organisations.id'))
    partner_id = Column(String, ForeignKey('partners.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Partner(Base):
    __tablename__ = 'partners'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    organisation_id = Column(String, ForeignKey('organisations.id'), nullable=False)
    contact_email = Column(String)
    status = Column(String, default='ACTIVE')
    created_at = Column(DateTime, default=datetime.utcnow)

class Schema(Base):
    __tablename__ = 'schemas'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    organisation_id = Column(String, ForeignKey('organisations.id'), nullable=False)
    partner_id = Column(String, ForeignKey('partners.id'), nullable=False)
    schema_name = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    status = Column(String, default='ACTIVE')
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, ForeignKey('users.id'))

class SchemaColumn(Base):
    __tablename__ = 'schema_columns'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    schema_id = Column(String, ForeignKey('schemas.id'), nullable=False)
    column_name = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    is_nullable = Column(Boolean, default=False)
    is_required = Column(Boolean, default=True)
    is_primary_key = Column(Boolean, default=False)
    format_pattern = Column(String, nullable=True)
    description = Column(String, nullable=True)
    order_index = Column(Integer, default=0)

class DataContract(Base):
    __tablename__ = 'data_contracts'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    organisation_id = Column(String, ForeignKey('organisations.id'), nullable=False)
    partner_id = Column(String, ForeignKey('partners.id'), nullable=False)
    contract_name = Column(String, nullable=False)
    version = Column(Integer, default=1)
    status = Column(String, default='ACTIVE')
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, ForeignKey('users.id'))

class ContractRule(Base):
    __tablename__ = 'contract_rules'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    contract_id = Column(String, ForeignKey('data_contracts.id'), nullable=False)
    column_name = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    is_required = Column(Boolean, default=True)
    is_nullable = Column(Boolean, default=False)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    allowed_values = Column(String, nullable=True)
    regex_pattern = Column(String, nullable=True)
    description = Column(String, nullable=True)

class PipelineRun(Base):
    __tablename__ = 'pipeline_runs'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    organisation_id = Column(String, ForeignKey('organisations.id'), nullable=False)
    partner_id = Column(String, ForeignKey('partners.id'), nullable=False)
    schema_version = Column(Integer)
    received_at = Column(DateTime, default=datetime.utcnow)
    validation_started_at = Column(DateTime, nullable=True)
    validation_completed_at = Column(DateTime, nullable=True)
    status = Column(String, default='RECEIVED')
    records_received = Column(Integer, default=0)
    records_valid = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)
    schema_change_count = Column(Integer, default=0)
    breaking_change_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    publication_status = Column(String, default='PENDING')
    failure_reason = Column(String, nullable=True)
    is_baseline = Column(Boolean, default=False)

class SchemaChange(Base):
    __tablename__ = 'schema_changes'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    pipeline_run_id = Column(String, ForeignKey('pipeline_runs.id'), nullable=False)
    change_type = Column(String, nullable=False)
    column_name = Column(String, nullable=False)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    severity = Column(String, nullable=False)
    category = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    recommendation = Column(String, nullable=True)

class DownstreamDependency(Base):
    __tablename__ = 'downstream_dependencies'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    organisation_id = Column(String, ForeignKey('organisations.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner = Column(String, nullable=True)
    criticality = Column(String, default='MEDIUM')
    created_at = Column(DateTime, default=datetime.utcnow)

class DependencyColumn(Base):
    __tablename__ = 'dependency_columns'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    dependency_id = Column(String, ForeignKey('downstream_dependencies.id'), nullable=False)
    column_name = Column(String, nullable=False)
    is_critical = Column(Boolean, default=True)

class PublicationDecision(Base):
    __tablename__ = 'publication_decisions'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    pipeline_run_id = Column(String, ForeignKey('pipeline_runs.id'), nullable=False)
    decision = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    decided_at = Column(DateTime, default=datetime.utcnow)
    decided_by = Column(String, nullable=True)
    breaking_changes = Column(Integer, default=0)
    affected_dependencies = Column(Integer, default=0)
    override_justification = Column(String, nullable=True)

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    organisation_id = Column(String, ForeignKey('organisations.id'), nullable=False)
    pipeline_run_id = Column(String, ForeignKey('pipeline_runs.id'), nullable=True)
    severity = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    organisation_id = Column(String, ForeignKey('organisations.id'), nullable=False)
    user_id = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=True)
    resource_id = Column(String, nullable=True)
    details = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    organisation_id = Column(String, ForeignKey('organisations.id'), nullable=True)
    respondent_role = Column(String, nullable=False)
    clarity_score = Column(Integer, nullable=False)
    usefulness_score = Column(Integer, nullable=False)
    schema_diff_clarity = Column(Integer, nullable=False)
    dashboard_helpfulness = Column(Integer, nullable=False)
    risk_reduction_confidence = Column(Integer, nullable=False)
    suggestions = Column(String, nullable=True)
    is_simulated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)