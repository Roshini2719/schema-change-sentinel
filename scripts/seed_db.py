import os
from app.database.connection import SessionLocal, init_db
from app.models.models import Organisation, User, Partner, Schema, SchemaColumn, DownstreamDependency, DependencyColumn, DataContract, ContractRule
from app.core.auth import get_password_hash

def seed():
    print("🌱 Seeding Schema Sentinel database...")
    init_db()
    db = SessionLocal()

    # Clear existing data if any
    db.query(DependencyColumn).delete()
    db.query(DownstreamDependency).delete()
    db.query(ContractRule).delete()
    db.query(DataContract).delete()
    db.query(SchemaColumn).delete()
    db.query(Schema).delete()
    db.query(User).delete()
    db.query(Partner).delete()
    db.query(Organisation).delete()
    db.commit()

    # 1. Organisations
    org1 = Organisation(name="FinBank Global", description="Primary Fintech Operating Entity")
    org2 = Organisation(name="PayStream Inc", description="Secondary Payment Processing Tenant")
    db.add_all([org1, org2])
    db.commit()

    # 2. Partners
    partner_a = Partner(name="Partner Alpha (Cards)", organisation_id=org1.id, contact_email="api@partnera.com")
    partner_b = Partner(name="Partner Beta (ACH)", organisation_id=org1.id, contact_email="tech@partnerb.com")
    db.add_all([partner_a, partner_b])
    db.commit()

    # 3. Users (RBAC)
    admin_user = User(
        email="admin@finbank.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Alice Admin",
        role="ADMIN",
        organisation_id=org1.id
    )
    eng_user = User(
        email="engineer@finbank.com",
        hashed_password=get_password_hash("engineer123"),
        full_name="Bob Engineer",
        role="DATA_ENGINEER",
        organisation_id=org1.id
    )
    analyst_user = User(
        email="analyst@finbank.com",
        hashed_password=get_password_hash("analyst123"),
        full_name="Charlie Analyst",
        role="ANALYST",
        organisation_id=org1.id
    )
    partner_user = User(
        email="partner@partnera.com",
        hashed_password=get_password_hash("partner123"),
        full_name="Dave Partner",
        role="PARTNER",
        organisation_id=org1.id,
        partner_id=partner_a.id
    )
    db.add_all([admin_user, eng_user, analyst_user, partner_user])
    db.commit()

    # 4. Registered Schemas
    schema_a = Schema(
        organisation_id=org1.id,
        partner_id=partner_a.id,
        schema_name="Partner A Card Transactions",
        version=1,
        created_by=eng_user.id
    )
    db.add(schema_a)
    db.commit()

    cols_a = [
        SchemaColumn(schema_id=schema_a.id, column_name="transaction_id", data_type="string", is_required=True, is_primary_key=True, order_index=0),
        SchemaColumn(schema_id=schema_a.id, column_name="amount", data_type="decimal", is_required=True, order_index=1),
        SchemaColumn(schema_id=schema_a.id, column_name="currency", data_type="string", is_required=True, order_index=2),
        SchemaColumn(schema_id=schema_a.id, column_name="timestamp", data_type="datetime", is_required=True, order_index=3),
        SchemaColumn(schema_id=schema_a.id, column_name="status", data_type="string", is_required=True, order_index=4),
    ]
    db.add_all(cols_a)

    # 5. Data Contract
    contract_a = DataContract(
        organisation_id=org1.id,
        partner_id=partner_a.id,
        contract_name="Card Transactions Ingestion Contract",
        version=1,
        created_by=eng_user.id
    )
    db.add(contract_a)
    db.commit()

    rules_a = [
        ContractRule(contract_id=contract_a.id, column_name="transaction_id", data_type="string", is_required=True, is_nullable=False),
        ContractRule(contract_id=contract_a.id, column_name="amount", data_type="decimal", is_required=True, min_value=0.01),
        ContractRule(contract_id=contract_a.id, column_name="currency", data_type="string", is_required=True, allowed_values='["USD","EUR","GBP","INR","CAD"]'),
    ]
    db.add_all(rules_a)

    # 6. Downstream Dependencies (Blast Radius Lineage)
    dep1 = DownstreamDependency(organisation_id=org1.id, name="Fraud Detection Engine", criticality="CRITICAL", owner="Security Team")
    dep2 = DownstreamDependency(organisation_id=org1.id, name="Daily Revenue Ledger", criticality="HIGH", owner="Finance Team")
    dep3 = DownstreamDependency(organisation_id=org1.id, name="Regulatory AML Compliance Report", criticality="CRITICAL", owner="Compliance")
    dep4 = DownstreamDependency(organisation_id=org1.id, name="Partner Settlement Pipeline", criticality="MEDIUM", owner="Operations")
    db.add_all([dep1, dep2, dep3, dep4])
    db.commit()

    dep_cols = [
        DependencyColumn(dependency_id=dep1.id, column_name="transaction_id", is_critical=True),
        DependencyColumn(dependency_id=dep1.id, column_name="amount", is_critical=True),
        DependencyColumn(dependency_id=dep2.id, column_name="amount", is_critical=True),
        DependencyColumn(dependency_id=dep2.id, column_name="currency", is_critical=True),
        DependencyColumn(dependency_id=dep3.id, column_name="transaction_id", is_critical=True),
        DependencyColumn(dependency_id=dep3.id, column_name="timestamp", is_critical=True),
        DependencyColumn(dependency_id=dep4.id, column_name="status", is_critical=False),
    ]
    db.add_all(dep_cols)

    db.commit()
    db.close()
    print("✅ Database successfully seeded with demo entities!")

if __name__ == "__main__":
    seed()
