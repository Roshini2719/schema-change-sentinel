from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database.connection import get_db
from ..models.models import Schema, SchemaColumn, Partner, PipelineRun, SchemaChange, PublicationDecision, Alert
from ..schemas.schemas import DemoScenarioRequest, DemoScenarioResponse
from ..core.auth import get_current_user, UserContext
from ..services.schema_sentinel import compare_schemas
from ..services.dependency_analyzer import analyze_impact
from ..services.risk_engine import RiskEngine

router = APIRouter(prefix="/api/demo", tags=["demo"])

SCENARIOS = {
    "SCENARIO_1_NORMAL": {
        "title": "Scenario 1: Normal Ingestion (Matching Schema)",
        "columns": [
            {"column_name": "transaction_id", "data_type": "string", "is_required": True, "is_primary_key": True},
            {"column_name": "amount", "data_type": "decimal", "is_required": True},
            {"column_name": "currency", "data_type": "string", "is_required": True},
            {"column_name": "timestamp", "data_type": "datetime", "is_required": True},
            {"column_name": "status", "data_type": "string", "is_required": True}
        ]
    },
    "SCENARIO_2_REMOVED_REQUIRED": {
        "title": "Scenario 2: Required Field Removed (transaction_id missing)",
        "columns": [
            {"column_name": "amount", "data_type": "decimal", "is_required": True},
            {"column_name": "currency", "data_type": "string", "is_required": True},
            {"column_name": "timestamp", "data_type": "datetime", "is_required": True},
            {"column_name": "status", "data_type": "string", "is_required": True}
        ]
    },
    "SCENARIO_3_TYPE_CHANGE": {
        "title": "Scenario 3: Data Type Incompatibility (amount decimal -> string)",
        "columns": [
            {"column_name": "transaction_id", "data_type": "string", "is_required": True, "is_primary_key": True},
            {"column_name": "amount", "data_type": "string", "is_required": True}, # Type shift
            {"column_name": "currency", "data_type": "string", "is_required": True},
            {"column_name": "timestamp", "data_type": "datetime", "is_required": True},
            {"column_name": "status", "data_type": "string", "is_required": True}
        ]
    },
    "SCENARIO_4_NULLABLE_SHIFT": {
        "title": "Scenario 4: Nullable Shift (amount required -> optional)",
        "columns": [
            {"column_name": "transaction_id", "data_type": "string", "is_required": True, "is_primary_key": True},
            {"column_name": "amount", "data_type": "decimal", "is_required": False}, # Nullable shift
            {"column_name": "currency", "data_type": "string", "is_required": True},
            {"column_name": "timestamp", "data_type": "datetime", "is_required": True},
            {"column_name": "status", "data_type": "string", "is_required": True}
        ]
    },
    "SCENARIO_5_EXTRA_METADATA": {
        "title": "Scenario 5: Non-Breaking Addition (extra metadata field)",
        "columns": [
            {"column_name": "transaction_id", "data_type": "string", "is_required": True, "is_primary_key": True},
            {"column_name": "amount", "data_type": "decimal", "is_required": True},
            {"column_name": "currency", "data_type": "string", "is_required": True},
            {"column_name": "timestamp", "data_type": "datetime", "is_required": True},
            {"column_name": "status", "data_type": "string", "is_required": True},
            {"column_name": "meta_device_ip", "data_type": "string", "is_required": False} # Added
        ]
    }
}

@router.post("/run-scenario", response_model=DemoScenarioResponse)
def run_scenario(
    req: DemoScenarioRequest,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scenario_data = SCENARIOS.get(req.scenario)
    if not scenario_data:
        raise HTTPException(status_code=400, detail="Invalid scenario key")

    partner = db.query(Partner).filter(Partner.organisation_id == current_user.organisation_id).first()
    if not partner:
        raise HTTPException(status_code=400, detail="Partner not found for organisation")

    registered_schema = db.query(Schema).filter(Schema.partner_id == partner.id).first()
    expected_cols = db.query(SchemaColumn).filter(SchemaColumn.schema_id == registered_schema.id).all() if registered_schema else []

    incoming_cols = scenario_data["columns"]
    changes = compare_schemas(expected_cols, incoming_cols)
    affected_deps = analyze_impact(db, current_user.organisation_id, changes)
    
    risk_res = RiskEngine.calculate_risk(changes, affected_deps)

    run = PipelineRun(
        organisation_id=current_user.organisation_id,
        partner_id=partner.id,
        schema_version=1,
        records_received=1000,
        records_valid=1000 if risk_res['decision'] == 'ALLOW' else 0,
        records_rejected=0 if risk_res['decision'] == 'ALLOW' else 1000,
        status="COMPLETED",
        validation_started_at=datetime.utcnow(),
        validation_completed_at=datetime.utcnow(),
        schema_change_count=len(changes),
        breaking_change_count=risk_res['breakdown']['breaking_changes_count'],
        publication_status="PUBLISHED" if risk_res['decision'] == 'ALLOW' else "BLOCKED",
        failure_reason=None if risk_res['decision'] == 'ALLOW' else risk_res['reason']
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    for c in changes:
        sc = SchemaChange(
            pipeline_run_id=run.id,
            change_type=c.change_type,
            column_name=c.column_name,
            old_value=c.old_value,
            new_value=c.new_value,
            severity=c.severity,
            category=c.category,
            reason=c.reason,
            recommendation=c.recommendation
        )
        db.add(sc)

    pub_dec = PublicationDecision(
        pipeline_run_id=run.id,
        decision=risk_res['decision'],
        reason=risk_res['reason'],
        breaking_changes=risk_res['breakdown']['breaking_changes_count'],
        affected_dependencies=risk_res['breakdown']['affected_dependencies_count']
    )
    db.add(pub_dec)
    db.commit()

    change_responses = [
        {
            "id": getattr(c, "id", None),
            "change_type": c.change_type,
            "column_name": c.column_name,
            "old_value": c.old_value,
            "new_value": c.new_value,
            "severity": c.severity,
            "category": c.category,
            "reason": c.reason,
            "recommendation": c.recommendation
        }
        for c in changes
    ]

    return {
        "run_id": run.id,
        "status": run.status,
        "changes": change_responses,
        "affected_dependencies": len(affected_deps),
        "publication_decision": risk_res['decision']
    }
