"""Seed data for Schema-Change Sentinel demo."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.models.partner import Partner
from app.models.data_source import DataSource
from app.models.schema import SchemaVersion
from app.models.contract import DataContract
from app.models.dependency import DownstreamDependency
from app.models.pipeline import PipelineRun
from app.auth.password import hash_password
import json
from datetime import datetime, timezone

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Create Orgs
        org_alpha = Organization(name="Fintech Alpha", status="active")
        org_beta = Organization(name="Fintech Beta", status="active")
        db.add_all([org_alpha, org_beta])
        db.commit()
        db.refresh(org_alpha)
        db.refresh(org_beta)

        # Create Users
        users = [
            User(organization_id=org_alpha.id, name="Admin Alpha", email="admin@alpha.com", password_hash=hash_password("admin123"), role=UserRole.ADMIN),
            User(organization_id=org_alpha.id, name="Engineer Alpha", email="engineer@alpha.com", password_hash=hash_password("engineer123"), role=UserRole.DATA_ENGINEER),
            User(organization_id=org_alpha.id, name="Analyst Alpha", email="analyst@alpha.com", password_hash=hash_password("analyst123"), role=UserRole.DATA_ANALYST),
            User(organization_id=org_alpha.id, name="Partner Alpha", email="partner@alpha.com", password_hash=hash_password("partner123"), role=UserRole.PARTNER),
            User(organization_id=org_beta.id, name="Admin Beta", email="admin@beta.com", password_hash=hash_password("beta123"), role=UserRole.ADMIN),
        ]
        db.add_all(users)
        db.commit()

        # Create Partners
        p_alpha = Partner(organization_id=org_alpha.id, name="Partner Alpha Payments", status="active", contact_email="alpha@partner.com")
        p_beta_bank = Partner(organization_id=org_alpha.id, name="Partner Beta Bank", status="active", contact_email="betabank@partner.com")
        p_gamma = Partner(organization_id=org_alpha.id, name="Partner Gamma Wallet", status="active", contact_email="gamma@partner.com")
        p_delta = Partner(organization_id=org_beta.id, name="Partner Delta Finance", status="active", contact_email="delta@partner.com")
        db.add_all([p_alpha, p_beta_bank, p_gamma, p_delta])
        db.commit()
        db.refresh(p_alpha)

        # Create Data Sources
        ds1 = DataSource(organization_id=org_alpha.id, partner_id=p_alpha.id, name="Transactions Stream", type="kafka", connection_details={"topic": "tx_events"})
        db.add(ds1)
        db.commit()
        db.refresh(ds1)

        # Create Schema
        schema_def = {
            "fields": {
                "transaction_id": {"type": "string", "required": True, "nullable": False, "primary_key": True},
                "customer_id": {"type": "string", "required": True, "nullable": False},
                "amount": {"type": "decimal", "required": True, "nullable": False},
                "currency": {"type": "string", "required": True, "nullable": False},
                "transaction_date": {"type": "datetime", "required": True, "nullable": False},
                "status": {"type": "enum", "required": True, "nullable": False, "values": ["SUCCESS", "FAILED", "PENDING"]},
            }
        }
        sv = SchemaVersion(data_source_id=ds1.id, version_hash="v1_hash", schema_definition=schema_def, status="approved")
        db.add(sv)
        db.commit()
        db.refresh(sv)

        # Create Contract
        rules = {"rules": [{"field": "amount", "type": "decimal"}]}
        contract = DataContract(data_source_id=ds1.id, schema_version_id=sv.id, rules=rules, is_active=True)
        db.add(contract)
        db.commit()

        # Create Dependency
        dep = DownstreamDependency(
            organization_id=org_alpha.id,
            data_source_id=ds1.id,
            name="Daily Currency Aggregation",
            type="dashboard",
            query_reference="SELECT currency, SUM(amount) FROM transactions GROUP BY currency",
            owner_email="analyst@alpha.com"
        )
        db.add(dep)
        db.commit()

        # Create Pipeline Run
        run = PipelineRun(
            data_source_id=ds1.id,
            schema_version_id=sv.id,
            status="success",
            records_processed=1000,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc)
        )
        db.add(run)
        db.commit()

        print("Seed data successfully created!")
        print(f"Created Organizations: Fintech Alpha, Fintech Beta")
        print(f"Created Users: admin@alpha.com, engineer@alpha.com, analyst@alpha.com, partner@alpha.com, admin@beta.com")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
