"""
Phase 1 — Synthetic Dataset Generator
Generates realistic fintech transaction schema versions for 3 partners.
Outputs:
  data/schemas/partner_a/schema_v1.json  (baseline)
  data/schemas/partner_a/schema_v2.json  (breaking: amount type changed)
  data/schemas/partner_a/schema_v3.json  (breaking: tx_id removed)
  data/schemas/partner_b/schema_v1.json
  data/schemas/partner_b/schema_v2.json  (non-breaking: column added)
  data/schemas/partner_c/schema_v1.json
  data/pipeline_runs.json                (50 simulated historical runs)
"""
import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent

def gen_id():
    return str(uuid.uuid4())[:8]

BASE_SCHEMA = [
    {"column_name": "transaction_id",  "data_type": "string",   "is_nullable": False, "is_required": True,  "is_primary_key": True,  "description": "Unique transaction identifier"},
    {"column_name": "amount",           "data_type": "decimal",  "is_nullable": False, "is_required": True,  "is_primary_key": False, "description": "Transaction amount"},
    {"column_name": "currency",         "data_type": "string",   "is_nullable": False, "is_required": True,  "is_primary_key": False, "description": "ISO 4217 currency code"},
    {"column_name": "partner_id",       "data_type": "string",   "is_nullable": False, "is_required": True,  "is_primary_key": False, "description": "Partner identifier"},
    {"column_name": "timestamp",        "data_type": "datetime", "is_nullable": False, "is_required": True,  "is_primary_key": False, "description": "Transaction timestamp (UTC)"},
    {"column_name": "merchant_id",      "data_type": "string",   "is_nullable": False, "is_required": True,  "is_primary_key": False, "description": "Merchant identifier"},
    {"column_name": "status",           "data_type": "string",   "is_nullable": False, "is_required": True,  "is_primary_key": False, "description": "PENDING|SETTLED|FAILED"},
    {"column_name": "card_last4",       "data_type": "string",   "is_nullable": True,  "is_required": False, "is_primary_key": False, "description": "Last 4 digits"},
    {"column_name": "ip_address",       "data_type": "string",   "is_nullable": True,  "is_required": False, "is_primary_key": False, "description": "Client IP"},
]

def schema_json(version, schema_name, partner, columns, breaking=False, notes=""):
    return {
        "schema_version": version,
        "schema_name": schema_name,
        "partner": partner,
        "generated_at": datetime.utcnow().isoformat(),
        "is_breaking": breaking,
        "notes": notes,
        "columns": columns,
    }

def write_schema(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
    print(f"  Written: {path}")

def generate_all():
    print("Generating synthetic schemas...")

    # ── Partner A (Stripe-like) ──────────────────────────────────────────────
    pa = ROOT / "schemas" / "partner_a"

    # v1: baseline
    write_schema(pa / "schema_v1.json", schema_json(
        "1.0.0", "PartnerA Transaction Schema", "PartnerA (Stripe)",
        BASE_SCHEMA, breaking=False,
        notes="Baseline schema. All required fields present."
    ))

    # v2: BREAKING — amount type changed to string
    v2_cols = [dict(c) for c in BASE_SCHEMA]
    for c in v2_cols:
        if c["column_name"] == "amount":
            c["data_type"] = "string"
    write_schema(pa / "schema_v2.json", schema_json(
        "2.0.0", "PartnerA Transaction Schema", "PartnerA (Stripe)",
        v2_cols, breaking=True,
        notes="BREAKING: amount type changed from decimal to string. Breaks all arithmetic."
    ))

    # v3: BREAKING — transaction_id removed
    v3_cols = [c for c in BASE_SCHEMA if c["column_name"] != "transaction_id"]
    write_schema(pa / "schema_v3.json", schema_json(
        "3.0.0", "PartnerA Transaction Schema", "PartnerA (Stripe)",
        v3_cols, breaking=True,
        notes="BREAKING: transaction_id (PK) removed."
    ))

    # ── Partner B (Plaid-like) ───────────────────────────────────────────────
    pb = ROOT / "schemas" / "partner_b"

    # v1: subset of base
    pb_v1_cols = BASE_SCHEMA[:7]
    write_schema(pb / "schema_v1.json", schema_json(
        "1.0.0", "PartnerB Transaction Schema", "PartnerB (Plaid)",
        pb_v1_cols, breaking=False,
        notes="Baseline schema for PartnerB."
    ))

    # v2: NON-BREAKING — new optional metadata column added
    pb_v2_cols = list(pb_v1_cols) + [
        {"column_name": "account_type", "data_type": "string", "is_nullable": True, "is_required": False, "is_primary_key": False, "description": "Account type (new)"}
    ]
    write_schema(pb / "schema_v2.json", schema_json(
        "2.0.0", "PartnerB Transaction Schema", "PartnerB (Plaid)",
        pb_v2_cols, breaking=False,
        notes="Non-breaking: new optional account_type column added."
    ))

    # ── Partner C (Visa-like) ────────────────────────────────────────────────
    pc = ROOT / "schemas" / "partner_c"

    # v1: standard
    pc_v1_cols = BASE_SCHEMA[:8]
    write_schema(pc / "schema_v1.json", schema_json(
        "1.0.0", "PartnerC Transaction Schema", "PartnerC (Visa)",
        pc_v1_cols, breaking=False,
        notes="PartnerC baseline schema."
    ))

    # ── Simulate 50 historical pipeline runs ─────────────────────────────────
    print("\nGenerating pipeline run history...")
    runs = []
    partners = ["PartnerA (Stripe)", "PartnerB (Plaid)", "PartnerC (Visa)"]
    # Distribution: ~70% of runs involve some schema change for baseline comparison
    for i in range(50):
        partner = random.choice(partners)
        is_breaking = random.random() < 0.35  # 35% breaking
        is_warning  = random.random() < 0.20  # 20% warning
        baseline_blocked  = is_breaking and random.random() < 0.3  # baseline only catches 30%
        sentinel_blocked  = is_breaking  # sentinel always catches breaking

        run = {
            "run_id": gen_id(),
            "partner": partner,
            "run_timestamp": (datetime.utcnow() - timedelta(days=random.randint(0,30), hours=random.randint(0,23))).isoformat(),
            "schema_version": f"{random.randint(1,3)}.0.0",
            "has_breaking_change": is_breaking,
            "has_warning_change": is_warning,
            "baseline_decision": "BLOCK" if baseline_blocked else "ALLOW",
            "sentinel_decision": "BLOCK" if sentinel_blocked else "ALLOW",
            "records_count": random.randint(1000, 500000),
            "latency_ms": round(random.uniform(5, 95), 2),
        }
        runs.append(run)

    (ROOT / "pipeline_runs.json").write_text(json.dumps(runs, indent=2))
    print(f"  Written: {ROOT / 'pipeline_runs.json'} ({len(runs)} runs)")

    # ── Summary ──────────────────────────────────────────────────────────────
    breaking_runs = sum(1 for r in runs if r["has_breaking_change"])
    baseline_blocked = sum(1 for r in runs if r["has_breaking_change"] and r["baseline_decision"] == "BLOCK")
    sentinel_blocked = sum(1 for r in runs if r["has_breaking_change"] and r["sentinel_decision"] == "BLOCK")
    total = len(runs)

    print(f"\n{'='*60}")
    print(f"Dataset Summary:")
    print(f"  Total pipeline runs: {total}")
    print(f"  Runs with breaking changes: {breaking_runs}")
    print(f"  Baseline blocked breaking: {baseline_blocked}/{breaking_runs} ({100*baseline_blocked//max(breaking_runs,1)}%)")
    print(f"  Sentinel blocked breaking: {sentinel_blocked}/{breaking_runs} ({100*sentinel_blocked//max(breaking_runs,1)}%)")
    unsafe_published_baseline = breaking_runs - baseline_blocked
    unsafe_published_sentinel = breaking_runs - sentinel_blocked
    print(f"\n  ⚠️  Unsafe publications (baseline): {unsafe_published_baseline}")
    print(f"  ✅ Unsafe publications (sentinel):  {unsafe_published_sentinel}")
    print(f"{'='*60}")

if __name__ == "__main__":
    generate_all()
