import json
import time
import urllib.request
import urllib.parse
from app.database.connection import SessionLocal
from app.models.models import User, Partner, Schema, SchemaColumn, DownstreamDependency, DependencyColumn
from app.services.schema_sentinel import compare_schemas
from app.services.dependency_analyzer import analyze_impact
from app.services.risk_engine import RiskEngine

def run_experiment():
    print("🔬 Running Baseline vs Schema Sentinel Experiment (1,000 Pipeline Runs)...")
    db = SessionLocal()
    user = db.query(User).first()
    partner = db.query(Partner).filter(Partner.organisation_id == user.organisation_id).first()
    schema = db.query(Schema).filter(Schema.partner_id == partner.id).first()
    expected_cols = db.query(SchemaColumn).filter(SchemaColumn.schema_id == schema.id).all() if schema else []

    base_cols = [
        {"column_name": "transaction_id", "data_type": "string", "is_required": True},
        {"column_name": "amount", "data_type": "decimal", "is_required": True},
        {"column_name": "currency", "data_type": "string", "is_required": True},
        {"column_name": "timestamp", "data_type": "datetime", "is_required": True},
    ]

    total_runs = 1000
    baseline_unsafe = 0
    sentinel_unsafe = 0
    sentinel_blocked = 0
    sentinel_times = []

    # Failure scenario distribution
    scenarios = [
        ("NORMAL", False),
        ("REMOVED_REQUIRED", True),
        ("TYPE_MISMATCH", True),
        ("NULLABLE_SHIFT", True),
        ("ADDED_OPTIONAL", False)
    ]

    for i in range(total_runs):
        sc_type, is_breaking = scenarios[i % len(scenarios)]
        inc_cols = [dict(c) for c in base_cols]

        if sc_type == "REMOVED_REQUIRED":
            inc_cols = [c for c in inc_cols if c["column_name"] != "transaction_id"]
        elif sc_type == "TYPE_MISMATCH":
            for c in inc_cols:
                if c["column_name"] == "amount":
                    c["data_type"] = "string"
        elif sc_type == "NULLABLE_SHIFT":
            for c in inc_cols:
                if c["column_name"] == "currency":
                    c["is_required"] = False
        elif sc_type == "ADDED_OPTIONAL":
            inc_cols.append({"column_name": "meta_field", "data_type": "string", "is_required": False})

        # Baseline: accepts non-empty schemas regardless of breaking changes
        if len(inc_cols) > 0:
            if is_breaking:
                baseline_unsafe += 1

        # Sentinel: deep contract + risk evaluation
        t0 = time.time()
        changes = compare_schemas(expected_cols, inc_cols)
        impact = analyze_impact(db, user.organisation_id, changes)
        risk = RiskEngine.calculate_risk(changes, impact)
        t1 = time.time()
        sentinel_times.append((t1 - t0) * 1000.0)

        if risk['decision'] == 'BLOCK':
            sentinel_blocked += 1
        elif is_breaking:
            sentinel_unsafe += 1

    db.close()

    baseline_pct = (baseline_unsafe / total_runs) * 100.0
    sentinel_pct = (sentinel_unsafe / total_runs) * 100.0
    avg_latency = sum(sentinel_times) / len(sentinel_times)

    print("\n=======================================================")
    print("📊 EXPERIMENT RESULTS (BASELINE VS SENTINEL)")
    print("=======================================================")
    print(f"Total Pipeline Runs Simulated : {total_runs}")
    print(f"Baseline Unsafe Publication Rate: {baseline_pct:.1f}% ({baseline_unsafe} runs)")
    print(f"Sentinel Unsafe Publication Rate: {sentinel_pct:.1f}% ({sentinel_unsafe} runs)")
    print(f"Sentinel Blocked Unsafe Runs    : {sentinel_blocked}")
    print(f"Mean Validation Latency         : {avg_latency:.2f} ms")
    print(f"Risk Reduction Factor           : {baseline_pct - sentinel_pct:.1f}% Improvement")
    print("=======================================================\n")

if __name__ == "__main__":
    run_experiment()
