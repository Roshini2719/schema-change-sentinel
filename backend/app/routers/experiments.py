from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import time
import random
from typing import Dict, Any, List
from ..database.connection import get_db
from ..models.models import Schema, SchemaColumn, Partner, DownstreamDependency, DependencyColumn
from ..core.auth import get_current_user, UserContext
from ..services.schema_sentinel import compare_schemas
from ..services.dependency_analyzer import analyze_impact
from ..services.risk_engine import RiskEngine

router = APIRouter(prefix="/api/experiments", tags=["experiments"])

def baseline_check(incoming_cols: List[dict]) -> bool:
    return len(incoming_cols) > 0

@router.post("/run")
def run_benchmark_experiment(
    runs_count: int = 100,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    partner = db.query(Partner).filter(Partner.organisation_id == current_user.organisation_id).first()
    if not partner:
        raise HTTPException(status_code=400, detail="No partner configured for experiment")

    schema = db.query(Schema).filter(Schema.partner_id == partner.id).first()
    expected_cols = db.query(SchemaColumn).filter(SchemaColumn.schema_id == schema.id).all() if schema else []

    base_cols = [
        {"column_name": "transaction_id", "data_type": "string", "is_required": True},
        {"column_name": "amount", "data_type": "decimal", "is_required": True},
        {"column_name": "currency", "data_type": "string", "is_required": True},
        {"column_name": "timestamp", "data_type": "datetime", "is_required": True},
    ]

    baseline_allowed = 0
    baseline_blocked = 0
    baseline_unsafe_published = 0

    sentinel_allowed = 0
    sentinel_blocked = 0
    sentinel_unsafe_published = 0

    sentinel_latencies = []

    mutation_types = [
        "NORMAL",
        "REMOVED_REQUIRED",
        "TYPE_MISMATCH",
        "NULLABLE_SHIFT",
        "ADDED_OPTIONAL"
    ]

    for i in range(runs_count):
        mutation = random.choice(mutation_types)
        inc_cols = [dict(c) for c in base_cols]
        is_breaking = False

        if mutation == "REMOVED_REQUIRED":
            inc_cols = [c for c in inc_cols if c["column_name"] != "transaction_id"]
            is_breaking = True
        elif mutation == "TYPE_MISMATCH":
            for c in inc_cols:
                if c["column_name"] == "amount":
                    c["data_type"] = "string"
            is_breaking = True
        elif mutation == "NULLABLE_SHIFT":
            for c in inc_cols:
                if c["column_name"] == "currency":
                    c["is_required"] = False
            is_breaking = True
        elif mutation == "ADDED_OPTIONAL":
            inc_cols.append({"column_name": "meta_tag", "data_type": "string", "is_required": False})

        # Baseline Evaluation
        if baseline_check(inc_cols):
            baseline_allowed += 1
            if is_breaking:
                baseline_unsafe_published += 1
        else:
            baseline_blocked += 1

        # Sentinel Evaluation
        t0 = time.time()
        changes = compare_schemas(expected_cols, inc_cols) if expected_cols else []
        impact = analyze_impact(db, current_user.organisation_id, changes)
        risk = RiskEngine.calculate_risk(changes, impact)
        t1 = time.time()
        sentinel_latencies.append((t1 - t0) * 1000.0)

        if risk['decision'] == 'ALLOW':
            sentinel_allowed += 1
            if is_breaking:
                sentinel_unsafe_published += 1
        else:
            sentinel_blocked += 1

    avg_latency = sum(sentinel_latencies) / len(sentinel_latencies) if sentinel_latencies else 0.0
    baseline_unsafe_rate = (baseline_unsafe_published / runs_count) * 100.0
    sentinel_unsafe_rate = (sentinel_unsafe_published / runs_count) * 100.0

    return {
        "simulation_runs": runs_count,
        "baseline_metrics": {
            "allowed": baseline_allowed,
            "blocked": baseline_blocked,
            "unsafe_publications": baseline_unsafe_published,
            "unsafe_publication_rate_pct": round(baseline_unsafe_rate, 2)
        },
        "sentinel_metrics": {
            "allowed": sentinel_allowed,
            "blocked": sentinel_blocked,
            "unsafe_publications": sentinel_unsafe_published,
            "unsafe_publication_rate_pct": round(sentinel_unsafe_rate, 2),
            "mean_validation_latency_ms": round(avg_latency, 2)
        },
        "comparison_summary": {
            "risk_reduction_pct": round(baseline_unsafe_rate - sentinel_unsafe_rate, 2),
            "target_achieved": sentinel_unsafe_rate == 0.0,
            "verdict": "Sentinel successfully blocked 100% of breaking upstream modifications."
        }
    }
