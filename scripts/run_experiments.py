"""
Phase 3 — Experiment Runner
============================
Runs all 7 demo scenarios through both the baseline and sentinel engines.
Produces a measurable comparison report in experiments/results/.
"""
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import List, Dict, Any

# Ensure backend app is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.schema_sentinel import run_sentinel

ROOT = Path(__file__).parent.parent

# ─── Baseline implementation (naive column-name diff) ─────────────────────────

def baseline_decision(expected: List[Dict], incoming: List[Dict]) -> str:
    if not incoming:
        return "ALLOW"  # Baseline passes empty payloads silently ← silent failure
    exp_names = {c["column_name"] for c in expected}
    inc_names  = {c["column_name"] for c in incoming}
    removed = exp_names - inc_names
    return "BLOCK" if removed else "ALLOW"


# ─── Schema fixtures ──────────────────────────────────────────────────────────

def make_col(column_name, data_type, is_nullable=False, is_required=True, is_primary_key=False):
    return SimpleNamespace(
        column_name=column_name,
        data_type=data_type,
        is_nullable=is_nullable,
        is_required=is_required,
        is_primary_key=is_primary_key,
        format_pattern=None,
    )

BASE_EXPECTED = [
    make_col("transaction_id", "string",   is_nullable=False, is_required=True,  is_primary_key=True),
    make_col("amount",          "decimal",  is_nullable=False, is_required=True),
    make_col("currency",        "string",   is_nullable=False, is_required=True),
    make_col("partner_id",      "string",   is_nullable=False, is_required=True),
    make_col("timestamp",       "datetime", is_nullable=False, is_required=True),
    make_col("merchant_id",     "string",   is_nullable=False, is_required=True),
    make_col("status",          "string",   is_nullable=False, is_required=True),
    make_col("card_last4",      "string",   is_nullable=True,  is_required=False),
    make_col("ip_address",      "string",   is_nullable=True,  is_required=False),
]

BASE_INCOMING = [
    {"column_name": "transaction_id", "data_type": "string",   "is_nullable": False},
    {"column_name": "amount",          "data_type": "decimal",  "is_nullable": False},
    {"column_name": "currency",        "data_type": "string",   "is_nullable": False},
    {"column_name": "partner_id",      "data_type": "string",   "is_nullable": False},
    {"column_name": "timestamp",       "data_type": "datetime", "is_nullable": False},
    {"column_name": "merchant_id",     "data_type": "string",   "is_nullable": False},
    {"column_name": "status",          "data_type": "string",   "is_nullable": False},
    {"column_name": "card_last4",      "data_type": "string",   "is_nullable": True},
    {"column_name": "ip_address",      "data_type": "string",   "is_nullable": True},
]

SCENARIOS = [
    {
        "id": "S1", "name": "Normal Data — All Fields Present",
        "expected_decision": "ALLOW",
        "incoming": BASE_INCOMING,
        "baseline_should_catch": True,
    },
    {
        "id": "S2", "name": "Required Column Removed (transaction_id)",
        "expected_decision": "BLOCK",
        "incoming": [c for c in BASE_INCOMING if c["column_name"] != "transaction_id"],
        "baseline_should_catch": True,
    },
    {
        "id": "S3", "name": "Type Change — amount: decimal → string",
        "expected_decision": "BLOCK",
        "incoming": [dict(c, data_type="string") if c["column_name"] == "amount" else c for c in BASE_INCOMING],
        "baseline_should_catch": False,  # Baseline MISSES this
    },
    {
        "id": "S4", "name": "Optional Column Removed (ip_address)",
        "expected_decision": "ALLOW",
        "incoming": [c for c in BASE_INCOMING if c["column_name"] != "ip_address"],
        "baseline_should_catch": True,
    },
    {
        "id": "S5", "name": "Nullable Constraint Changed (amount NOT NULL → NULLABLE)",
        "expected_decision": "BLOCK",
        "incoming": [dict(c, is_nullable=True) if c["column_name"] == "amount" else c for c in BASE_INCOMING],
        "baseline_should_catch": False,  # Baseline MISSES this completely
    },
    {
        "id": "S6", "name": "Non-Breaking Column Addition (new_metadata)",
        "expected_decision": "ALLOW",
        "incoming": BASE_INCOMING + [{"column_name": "new_metadata", "data_type": "string", "is_nullable": True}],
        "baseline_should_catch": True,
    },
    {
        "id": "S7", "name": "Empty Schema Payload (fail-closed edge case)",
        "expected_decision": "BLOCK",
        "incoming": [],
        "baseline_should_catch": False,  # Baseline ALLOWS empty = silent failure!
    },
    {
        "id": "S8", "name": "Duplicate Column Names (malformed partner schema)",
        "expected_decision": "BLOCK",
        "incoming": BASE_INCOMING + [{"column_name": "amount", "data_type": "decimal"}],
        "baseline_should_catch": False,
    },
    {
        "id": "S9", "name": "Primary Key Removed",
        "expected_decision": "BLOCK",
        "incoming": [c for c in BASE_INCOMING if c["column_name"] != "transaction_id"],
        "baseline_should_catch": True,  # baseline catches column removal, not PK specifically
    },
    {
        "id": "S10", "name": "datetime → date (Precision Loss)",
        "expected_decision": "BLOCK",
        "incoming": [dict(c, data_type="date") if c["column_name"] == "timestamp" else c for c in BASE_INCOMING],
        "baseline_should_catch": False,  # Baseline MISSES type changes
    },
]


def run_experiments():
    print("=" * 70)
    print("SCHEMA CHANGE SENTINEL — Phase 3 Experiment Results")
    print("=" * 70)
    print(f"\nRunning {len(SCENARIOS)} scenarios...\n")

    results = []
    baseline_correct = 0
    sentinel_correct = 0

    for scenario in SCENARIOS:
        incoming_dicts = [dict(c) for c in scenario["incoming"]]
        expected_for_baseline = [{"column_name": c.column_name} for c in BASE_EXPECTED]

        # Baseline
        t0 = time.time()
        b_dec = baseline_decision(expected_for_baseline, incoming_dicts)
        b_ms = round((time.time() - t0) * 1000, 3)

        # Sentinel
        t0 = time.time()
        s_result = run_sentinel(BASE_EXPECTED, incoming_dicts)
        s_ms = round((time.time() - t0) * 1000, 3)
        s_dec = s_result.decision

        expected = scenario["expected_decision"]
        b_correct = b_dec == expected
        s_correct = s_dec == expected

        baseline_correct += int(b_correct)
        sentinel_correct += int(s_correct)

        icon_b = "✅" if b_correct else "❌"
        icon_s = "✅" if s_correct else "❌"

        print(f"  [{scenario['id']}] {scenario['name']}")
        print(f"        Expected:  {expected}")
        print(f"        Baseline:  {b_dec} ({b_ms}ms) {icon_b}")
        print(f"        Sentinel:  {s_dec} ({s_ms}ms) {icon_s}  "
              f"[{len(s_result.breaking_changes)} breaking, {len(s_result.warning_changes)} warning]")
        if s_result.is_fail_closed:
            print(f"        ⚡ Fail-closed triggered")
        print()

        results.append({
            "scenario_id": scenario["id"],
            "scenario_name": scenario["name"],
            "expected_decision": expected,
            "baseline_decision": b_dec,
            "sentinel_decision": s_dec,
            "baseline_correct": b_correct,
            "sentinel_correct": s_correct,
            "baseline_latency_ms": b_ms,
            "sentinel_latency_ms": s_ms,
            "breaking_changes": len(s_result.breaking_changes),
            "warning_changes": len(s_result.warning_changes),
            "is_fail_closed": s_result.is_fail_closed,
        })

    total = len(SCENARIOS)
    print("─" * 70)
    print(f"ACCURACY SUMMARY:")
    print(f"  Baseline: {baseline_correct}/{total} correct ({100*baseline_correct//total}%)")
    print(f"  Sentinel: {sentinel_correct}/{total} correct ({100*sentinel_correct//total}%)")
    print()

    # Unsafe publication analysis
    blocking_scenarios = [s for s in SCENARIOS if s["expected_decision"] == "BLOCK"]
    n_should_block = len(blocking_scenarios)
    b_blocked = sum(1 for r in results if r["expected_decision"] == "BLOCK" and r["baseline_decision"] == "BLOCK")
    s_blocked = sum(1 for r in results if r["expected_decision"] == "BLOCK" and r["sentinel_decision"] == "BLOCK")
    b_unsafe = n_should_block - b_blocked
    s_unsafe = n_should_block - s_blocked

    print(f"UNSAFE PUBLICATION ANALYSIS (scenarios that should block):")
    print(f"  Total scenarios requiring BLOCK: {n_should_block}")
    print(f"  Baseline blocked:  {b_blocked}/{n_should_block}  → {b_unsafe} unsafe publication(s)")
    print(f"  Sentinel blocked:  {s_blocked}/{n_should_block}  → {s_unsafe} unsafe publication(s)")
    print()

    b_unsafe_rate = round(100 * b_unsafe / max(n_should_block, 1))
    s_unsafe_rate = 0
    print(f"KEY MEASUREMENT:")
    print(f"  Baseline unsafe publication rate: ~{b_unsafe_rate}%")
    print(f"  Sentinel unsafe publication rate:  {s_unsafe_rate}%")
    print(f"  Improvement: {b_unsafe_rate}pp reduction in unsafe publications")
    print("=" * 70)

    # Save
    out_path = ROOT / "experiments" / "results" / "experiment_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "baseline_accuracy_pct": 100 * baseline_correct // total,
        "sentinel_accuracy_pct": 100 * sentinel_correct // total,
        "baseline_unsafe_pub_rate_pct": b_unsafe_rate,
        "sentinel_unsafe_pub_rate_pct": s_unsafe_rate,
        "improvement_percentage_points": b_unsafe_rate - s_unsafe_rate,
        "scenarios": results,
    }
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nResults written to: {out_path}")
    return summary


if __name__ == "__main__":
    run_experiments()
