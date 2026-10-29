"""
Demo / Scenarios router
Provides 7 pre-built demo scenarios that can be run from the UI.
"""
import time
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.models import get_db, DataSchema
from ..core.auth import get_current_user, UserContext
from ..services.schema_sentinel import run_sentinel

router = APIRouter(prefix="/api/demo", tags=["demo"])

SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "s1",
        "name": "✅ Normal Data — All Fields Present",
        "description": "Complete, conformant schema. Should be published.",
        "expected_decision": "ALLOW",
        "incoming": [
            {"column_name": "transaction_id",  "data_type": "string",   "is_nullable": False, "is_required": True,  "is_primary_key": True},
            {"column_name": "amount",           "data_type": "decimal",  "is_nullable": False, "is_required": True,  "is_primary_key": False},
            {"column_name": "currency",         "data_type": "string",   "is_nullable": False, "is_required": True,  "is_primary_key": False},
            {"column_name": "partner_id",       "data_type": "string",   "is_nullable": False, "is_required": True,  "is_primary_key": False},
            {"column_name": "timestamp",        "data_type": "datetime", "is_nullable": False, "is_required": True,  "is_primary_key": False},
            {"column_name": "merchant_id",      "data_type": "string",   "is_nullable": False, "is_required": True,  "is_primary_key": False},
            {"column_name": "status",           "data_type": "string",   "is_nullable": False, "is_required": True,  "is_primary_key": False},
            {"column_name": "card_last4",       "data_type": "string",   "is_nullable": True,  "is_required": False, "is_primary_key": False},
            {"column_name": "ip_address",       "data_type": "string",   "is_nullable": True,  "is_required": False, "is_primary_key": False},
        ],
    },
    {
        "id": "s2",
        "name": "🚫 Required Column Removed (transaction_id)",
        "description": "Partner removed the primary key. CRITICAL BREAKING change.",
        "expected_decision": "BLOCK",
        "incoming": [
            {"column_name": "amount",      "data_type": "decimal",  "is_nullable": False},
            {"column_name": "currency",    "data_type": "string",   "is_nullable": False},
            {"column_name": "partner_id",  "data_type": "string",   "is_nullable": False},
            {"column_name": "timestamp",   "data_type": "datetime", "is_nullable": False},
            {"column_name": "merchant_id", "data_type": "string",   "is_nullable": False},
            {"column_name": "status",      "data_type": "string",   "is_nullable": False},
        ],
    },
    {
        "id": "s3",
        "name": "🚫 Type Change — amount: decimal → string",
        "description": "Amount field type changed to string. Breaks all arithmetic queries.",
        "expected_decision": "BLOCK",
        "incoming": [
            {"column_name": "transaction_id", "data_type": "string",   "is_nullable": False},
            {"column_name": "amount",          "data_type": "string",   "is_nullable": False},  # CHANGED
            {"column_name": "currency",        "data_type": "string",   "is_nullable": False},
            {"column_name": "partner_id",      "data_type": "string",   "is_nullable": False},
            {"column_name": "timestamp",       "data_type": "datetime", "is_nullable": False},
            {"column_name": "merchant_id",     "data_type": "string",   "is_nullable": False},
            {"column_name": "status",          "data_type": "string",   "is_nullable": False},
        ],
    },
    {
        "id": "s4",
        "name": "⚠️ Optional Column Removed (ip_address)",
        "description": "ip_address (optional) removed. WARNING — downstream fraud model may be affected.",
        "expected_decision": "ALLOW",
        "incoming": [
            {"column_name": "transaction_id", "data_type": "string",   "is_nullable": False},
            {"column_name": "amount",          "data_type": "decimal",  "is_nullable": False},
            {"column_name": "currency",        "data_type": "string",   "is_nullable": False},
            {"column_name": "partner_id",      "data_type": "string",   "is_nullable": False},
            {"column_name": "timestamp",       "data_type": "datetime", "is_nullable": False},
            {"column_name": "merchant_id",     "data_type": "string",   "is_nullable": False},
            {"column_name": "status",          "data_type": "string",   "is_nullable": False},
            {"column_name": "card_last4",      "data_type": "string",   "is_nullable": True},
            # ip_address REMOVED (optional)
        ],
    },
    {
        "id": "s5",
        "name": "🚫 Nullable Constraint Changed (amount: NOT NULL → NULLABLE)",
        "description": "Required amount field made nullable. Downstream NOT NULL constraints will break.",
        "expected_decision": "BLOCK",
        "incoming": [
            {"column_name": "transaction_id", "data_type": "string",   "is_nullable": False},
            {"column_name": "amount",          "data_type": "decimal",  "is_nullable": True},   # CHANGED
            {"column_name": "currency",        "data_type": "string",   "is_nullable": False},
            {"column_name": "partner_id",      "data_type": "string",   "is_nullable": False},
            {"column_name": "timestamp",       "data_type": "datetime", "is_nullable": False},
            {"column_name": "merchant_id",     "data_type": "string",   "is_nullable": False},
            {"column_name": "status",          "data_type": "string",   "is_nullable": False},
        ],
    },
    {
        "id": "s6",
        "name": "✅ Non-Breaking Addition (new_metadata column)",
        "description": "Optional column added. Non-breaking — allow and register.",
        "expected_decision": "ALLOW",
        "incoming": [
            {"column_name": "transaction_id",  "data_type": "string",   "is_nullable": False},
            {"column_name": "amount",           "data_type": "decimal",  "is_nullable": False},
            {"column_name": "currency",         "data_type": "string",   "is_nullable": False},
            {"column_name": "partner_id",       "data_type": "string",   "is_nullable": False},
            {"column_name": "timestamp",        "data_type": "datetime", "is_nullable": False},
            {"column_name": "merchant_id",      "data_type": "string",   "is_nullable": False},
            {"column_name": "status",           "data_type": "string",   "is_nullable": False},
            {"column_name": "card_last4",       "data_type": "string",   "is_nullable": True},
            {"column_name": "ip_address",       "data_type": "string",   "is_nullable": True},
            {"column_name": "new_metadata",     "data_type": "string",   "is_nullable": True},  # NEW
        ],
    },
    {
        "id": "s7",
        "name": "🚫 Empty/Malformed Schema (Edge Case)",
        "description": "Partner sends empty schema payload. Sentinel fails-closed and blocks publication.",
        "expected_decision": "BLOCK",
        "incoming": [],
    },
]

@router.get("/scenarios")
def list_scenarios():
    return [{"id": s["id"], "name": s["name"], "description": s["description"], "expected_decision": s["expected_decision"]} for s in SCENARIOS]

@router.post("/scenarios/{scenario_id}/run")
def run_scenario(
    scenario_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    scenario = next((s for s in SCENARIOS if s["id"] == scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Get first active schema for this org (demo shortcut)
    schema = db.query(DataSchema).filter(
        DataSchema.organisation_id == current_user.organisation_id,
        DataSchema.is_active == True,
    ).first()
    if not schema:
        raise HTTPException(status_code=404, detail="No active schema found for your organisation")

    from ..models.models import DownstreamDependency
    dependencies = db.query(DownstreamDependency).filter(
        DownstreamDependency.schema_id == schema.id
    ).all()

    t0 = time.time()
    decision = run_sentinel(schema.columns, scenario["incoming"], dependencies)
    elapsed_ms = round((time.time() - t0) * 1000, 2)

    correct = decision.decision == scenario["expected_decision"]

    return {
        "scenario_id": scenario_id,
        "scenario_name": scenario["name"],
        "expected_decision": scenario["expected_decision"],
        "actual_decision": decision.decision,
        "correct": correct,
        "reason": decision.reason,
        "breaking_changes_count": len(decision.breaking_changes),
        "warning_changes_count": len(decision.warning_changes),
        "info_changes_count": len(decision.info_changes),
        "is_fail_closed": decision.is_fail_closed,
        "affected_consumers": decision.affected_consumers,
        "breaking_changes": [
            {
                "change_type": c.change_type,
                "column_name": c.column_name,
                "old_value": c.old_value,
                "new_value": c.new_value,
                "severity": c.severity,
                "reason": c.reason,
                "recommendation": c.recommendation,
                "affected_consumers": c.affected_consumers,
            }
            for c in decision.breaking_changes
        ],
        "warning_changes": [
            {
                "change_type": c.change_type,
                "column_name": c.column_name,
                "severity": c.severity,
                "reason": c.reason,
                "affected_consumers": c.affected_consumers,
            }
            for c in decision.warning_changes
        ],
        "latency_ms": elapsed_ms,
    }
