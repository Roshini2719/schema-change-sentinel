import os
import textwrap

PROJECT_ROOT = "/Users/muthamilroshini/.gemini/antigravity/scratch/schema-sentinel"

FILES = {}

FILES["backend/requirements.txt"] = """
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pandas==2.1.4
pyarrow==14.0.2
pytest==7.4.3
httpx==0.25.2
aiofiles==23.2.1
""".strip()

FILES["backend/app/__init__.py"] = ""
FILES["backend/app/core/__init__.py"] = ""

FILES["backend/app/core/config.py"] = """
class Settings:
    SECRET_KEY: str = 'schema-sentinel-demo-secret-key-change-in-production'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    DATABASE_URL: str = 'sqlite:///./schema_sentinel.db'
    DEMO_MODE: bool = True

settings = Settings()
""".strip()

FILES["backend/app/core/auth.py"] = """
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from enum import Enum
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class Roles(str, Enum):
    ADMIN = "ADMIN"
    DATA_ENGINEER = "DATA_ENGINEER"
    ANALYST = "ANALYST"
    PARTNER = "PARTNER"

class UserContext:
    def __init__(self, user_id: str, email: str, role: str, organisation_id: str):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.organisation_id = organisation_id

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserContext:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        organisation_id: str = payload.get("organisation_id")
        if user_id is None or email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return UserContext(user_id=user_id, email=email, role=role, organisation_id=organisation_id)

def role_required(allowed_roles: List[Roles]):
    def role_checker(current_user: UserContext = Depends(get_current_user)):
        if current_user.role not in [r.value for r in allowed_roles]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return current_user
    return role_checker
""".strip()

FILES["backend/app/database/__init__.py"] = ""

FILES["backend/app/database/connection.py"] = """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ..core.config import settings

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
""".strip()

FILES["backend/app/models/__init__.py"] = ""

FILES["backend/app/models/models.py"] = """
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
""".strip()

def main():
    for rel_path, content in FILES.items():
        full_path = os.path.join(PROJECT_ROOT, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
    print("Scaffold complete.")

if __name__ == "__main__":
    main()
