"""
Database seeder — creates demo organisations, partners, users, schemas, contracts and dependencies.
Run once at startup in DEMO_MODE.
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.models import (
    Organisation, User, Partner, DataSchema, SchemaColumn,
    DataContract, DownstreamDependency, PipelineRun
)
from ..core.auth import get_password_hash

logger = logging.getLogger(__name__)

DEMO_ORGS = [
    {"name": "FinBank Corp", "description": "Primary fintech organisation"},
    {"name": "ClearPay Ltd",  "description": "Secondary fintech company"},
]

DEMO_PARTNERS = [
    {"name": "PartnerA (Stripe)", "org": "FinBank Corp", "email": "data@partnera.com"},
    {"name": "PartnerB (Plaid)",  "org": "FinBank Corp", "email": "data@partnerb.com"},
    {"name": "PartnerC (Visa)",   "org": "ClearPay Ltd", "email": "data@partnerc.com"},
]

DEMO_USERS = [
    {"email": "admin@finbank.com",    "password": "admin123",    "name": "Alice Admin",    "role": "ADMIN",          "org": "FinBank Corp"},
    {"email": "engineer@finbank.com", "password": "engineer123", "name": "Bob Engineer",   "role": "DATA_ENGINEER",  "org": "FinBank Corp"},
    {"email": "analyst@finbank.com",  "password": "analyst123",  "name": "Carol Analyst",  "role": "ANALYST",        "org": "FinBank Corp"},
    {"email": "partner@partnera.com", "password": "partner123",  "name": "Dave Partner",   "role": "PARTNER",        "org": "FinBank Corp", "partner": "PartnerA (Stripe)"},
    {"email": "admin@clearpay.com",   "password": "admin123",    "name": "Eve Admin",      "role": "ADMIN",          "org": "ClearPay Ltd"},
    {"email": "partner@partnerc.com", "password": "partner123",  "name": "Frank Partner",  "role": "PARTNER",        "org": "ClearPay Ltd", "partner": "PartnerC (Visa)"},
]

# Base transaction schema (v1 — the "registered" contract schema)
BASE_SCHEMA_COLUMNS = [
    {"column_name": "transaction_id",   "data_type": "string",  "is_nullable": False, "is_required": True,  "is_primary_key": True,  "description": "Unique transaction identifier"},
    {"column_name": "amount",           "data_type": "decimal", "is_nullable": False, "is_required": True,  "is_primary_key": False, "description": "Transaction amount in base currency"},
    {"column_name": "currency",         "data_type": "string",  "is_nullable": False, "is_required": True,  "is_primary_key": False, "description": "ISO 4217 currency code"},
    {"column_name": "partner_id",       "data_type": "string",  "is_nullable": False, "is_required": True,  "is_primary_key": False, "description": "Partner identifier"},
    {"column_name": "timestamp",        "data_type": "datetime","is_nullable": False, "is_required": True,  "is_primary_key": False, "description": "Transaction timestamp (UTC)"},
    {"column_name": "merchant_id",      "data_type": "string",  "is_nullable": False, "is_required": True,  "is_primary_key": False, "description": "Merchant identifier"},
    {"column_name": "status",           "data_type": "string",  "is_nullable": False, "is_required": True,  "is_primary_key": False, "description": "Transaction status: PENDING|SETTLED|FAILED"},
    {"column_name": "card_last4",       "data_type": "string",  "is_nullable": True,  "is_required": False, "is_primary_key": False, "description": "Last 4 digits of card"},
    {"column_name": "ip_address",       "data_type": "string",  "is_nullable": True,  "is_required": False, "is_primary_key": False, "description": "Client IP address"},
]

DOWNSTREAM_DEPS = [
    {"consumer_name": "Daily Settlement Report",  "consumer_type": "REPORT",    "criticality": "CRITICAL", "cols": ["transaction_id", "amount", "currency", "status", "timestamp"]},
    {"consumer_name": "Fraud Detection Model",    "consumer_type": "ML_MODEL",  "criticality": "CRITICAL", "cols": ["transaction_id", "amount", "merchant_id", "ip_address", "timestamp"]},
    {"consumer_name": "Revenue Dashboard",        "consumer_type": "DASHBOARD", "criticality": "HIGH",     "cols": ["amount", "currency", "status", "timestamp"]},
    {"consumer_name": "Regulatory Compliance ETL","consumer_type": "ETL",       "criticality": "CRITICAL", "cols": ["transaction_id", "amount", "currency", "partner_id", "timestamp"]},
    {"consumer_name": "Partner Reconciliation API","consumer_type": "API",      "criticality": "HIGH",     "cols": ["transaction_id", "partner_id", "amount", "status"]},
]

def seed_database(db: Session) -> None:
    if db.query(Organisation).first():
        logger.info("Database already seeded, skipping.")
        return

    logger.info("Seeding demo database...")

    # Organisations
    orgs = {}
    for od in DEMO_ORGS:
        o = Organisation(name=od["name"], description=od["description"])
        db.add(o)
        db.flush()
        orgs[od["name"]] = o

    # Partners
    partners = {}
    for pd in DEMO_PARTNERS:
        p = Partner(
            name=pd["name"],
            organisation_id=orgs[pd["org"]].id,
            contact_email=pd["email"],
            status="ACTIVE"
        )
        db.add(p)
        db.flush()
        partners[pd["name"]] = p

    # Users
    for ud in DEMO_USERS:
        partner_id = None
        if "partner" in ud:
            partner_id = partners[ud["partner"]].id
        u = User(
            email=ud["email"],
            hashed_password=get_password_hash(ud["password"]),
            full_name=ud["name"],
            role=ud["role"],
            organisation_id=orgs[ud["org"]].id,
            partner_id=partner_id,
        )
        db.add(u)

    # Schema (v1 — PartnerA)
    schema = DataSchema(
        name="PartnerA Transaction Schema v1",
        version="1.0.0",
        partner_id=partners["PartnerA (Stripe)"].id,
        organisation_id=orgs["FinBank Corp"].id,
        is_active=True,
        created_by="admin@finbank.com",
    )
    db.add(schema)
    db.flush()

    for col_data in BASE_SCHEMA_COLUMNS:
        col = SchemaColumn(schema_id=schema.id, **col_data)
        db.add(col)

    # Contract
    contract = DataContract(
        name="PartnerA Transaction Contract",
        partner_id=partners["PartnerA (Stripe)"].id,
        organisation_id=orgs["FinBank Corp"].id,
        registered_schema_id=schema.id,
        sla_hours=24,
        status="ACTIVE",
    )
    db.add(contract)

    # Downstream dependencies
    for dd in DOWNSTREAM_DEPS:
        dep = DownstreamDependency(
            schema_id=schema.id,
            organisation_id=orgs["FinBank Corp"].id,
            consumer_name=dd["consumer_name"],
            consumer_type=dd["consumer_type"],
            criticality=dd["criticality"],
            columns_used=dd["cols"],
            owner_email="engineer@finbank.com",
        )
        db.add(dep)

    # PartnerB minimal schema (ClearPay)
    schema_b = DataSchema(
        name="PartnerC Transaction Schema v1",
        version="1.0.0",
        partner_id=partners["PartnerC (Visa)"].id,
        organisation_id=orgs["ClearPay Ltd"].id,
        is_active=True,
        created_by="admin@clearpay.com",
    )
    db.add(schema_b)
    db.flush()
    for col_data in BASE_SCHEMA_COLUMNS[:6]:
        col = SchemaColumn(schema_id=schema_b.id, **col_data)
        db.add(col)

    db.commit()
    logger.info("Demo database seeded successfully.")
