"""
Test suite for Schema Change Sentinel
======================================
Tests cover:
1. Normal (conformant) schema — ALLOW
2. Required column removed — BLOCK
3. Type change incompatible — BLOCK
4. Type change compatible (widening) — ALLOW/INFO
5. Optional column removed — WARNING (ALLOW)
6. Nullable constraint changed on required field — BLOCK
7. Empty incoming schema (fail-closed) — BLOCK
8. Malformed incoming (non-list) — BLOCK
9. Duplicate column in incoming — BLOCK
10. New optional column added — INFO (ALLOW)
11. All required columns removed simultaneously — BLOCK
12. Primary key removed — BLOCK
"""
import pytest
from types import SimpleNamespace
from app.services.schema_sentinel import (
    run_sentinel, compare_schemas, make_gate_decision,
    SchemaChangeEvent, GateDecision, ChangeCategory
)

# ─── Helpers ──────────────────────────────────────────────────────────────────

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


# ─── Test 1: Normal schema ────────────────────────────────────────────────────

def test_normal_schema_allows_publication():
    """Scenario 1: Complete conformant schema → ALLOW."""
    decision = run_sentinel(BASE_EXPECTED, BASE_INCOMING)
    assert decision.decision == "ALLOW"
    assert len(decision.breaking_changes) == 0
    assert decision.is_fail_closed is False


# ─── Test 2: Required column removed ─────────────────────────────────────────

def test_required_column_removed_blocks():
    """Scenario 2: Remove required 'amount' column → BLOCK."""
    incoming = [c for c in BASE_INCOMING if c["column_name"] != "amount"]
    decision = run_sentinel(BASE_EXPECTED, incoming)
    assert decision.decision == "BLOCK"
    assert any(c.column_name == "amount" and c.change_type == "COLUMN_REMOVED"
               for c in decision.breaking_changes)


# ─── Test 3: Incompatible type change ────────────────────────────────────────

def test_incompatible_type_change_blocks():
    """Scenario 3: amount decimal → string → BLOCK."""
    incoming = [
        dict(c, data_type="string") if c["column_name"] == "amount" else c
        for c in BASE_INCOMING
    ]
    decision = run_sentinel(BASE_EXPECTED, incoming)
    assert decision.decision == "BLOCK"
    assert any(c.column_name == "amount" and c.change_type == "TYPE_CHANGED"
               for c in decision.breaking_changes)


# ─── Test 4: Compatible type widening ────────────────────────────────────────

def test_compatible_type_widening_allows():
    """integer → decimal is a widening, should be INFO not BREAKING."""
    expected = [make_col("tx_id", "string"), make_col("count", "integer")]
    incoming = [{"column_name": "tx_id", "data_type": "string"},
                {"column_name": "count", "data_type": "decimal"}]
    decision = run_sentinel(expected, incoming)
    assert decision.decision == "ALLOW"
    info_types = [c.change_type for c in decision.info_changes]
    assert "TYPE_CHANGED" in info_types


# ─── Test 5: Optional column removed ─────────────────────────────────────────

def test_optional_column_removed_warns_but_allows():
    """Scenario 4: ip_address (optional) removed → WARNING, still ALLOW."""
    incoming = [c for c in BASE_INCOMING if c["column_name"] != "ip_address"]
    decision = run_sentinel(BASE_EXPECTED, incoming)
    assert decision.decision == "ALLOW"
    assert any(c.column_name == "ip_address" for c in decision.warning_changes)


# ─── Test 6: Nullable constraint changed ─────────────────────────────────────

def test_nullable_changed_on_required_field_blocks():
    """Scenario 5: amount NOT NULL → NULLABLE → BLOCK."""
    incoming = [
        dict(c, is_nullable=True) if c["column_name"] == "amount" else c
        for c in BASE_INCOMING
    ]
    decision = run_sentinel(BASE_EXPECTED, incoming)
    assert decision.decision == "BLOCK"
    assert any(c.change_type == "NULLABLE_CHANGED" for c in decision.breaking_changes)


# ─── Test 7: Empty incoming schema (fail-closed) ──────────────────────────────

def test_empty_incoming_schema_fails_closed():
    """Scenario 7: Empty payload → BLOCK (fail-closed)."""
    decision = run_sentinel(BASE_EXPECTED, [])
    assert decision.decision == "BLOCK"
    assert decision.is_fail_closed is True


# ─── Test 8: Malformed incoming (non-list) ────────────────────────────────────

def test_malformed_incoming_fails_closed():
    """Edge case: incoming is a dict, not a list → BLOCK (fail-closed)."""
    decision = run_sentinel(BASE_EXPECTED, {"column_name": "bad"})  # type: ignore
    assert decision.decision == "BLOCK"
    assert decision.is_fail_closed is True


# ─── Test 9: Duplicate column in incoming ─────────────────────────────────────

def test_duplicate_column_blocks():
    """Edge case: duplicate column names in incoming schema → BLOCK."""
    incoming = BASE_INCOMING + [{"column_name": "amount", "data_type": "decimal"}]
    decision = run_sentinel(BASE_EXPECTED, incoming)
    assert decision.decision == "BLOCK"
    assert any(c.change_type == "DUPLICATE_COLUMN" for c in decision.breaking_changes)


# ─── Test 10: Non-breaking column addition ────────────────────────────────────

def test_new_optional_column_is_info_not_breaking():
    """Scenario 6: New optional column added → INFO, still ALLOW."""
    incoming = BASE_INCOMING + [{"column_name": "new_meta", "data_type": "string", "is_nullable": True}]
    decision = run_sentinel(BASE_EXPECTED, incoming)
    assert decision.decision == "ALLOW"
    assert any(c.column_name == "new_meta" and c.change_type == "COLUMN_ADDED"
               for c in decision.info_changes)


# ─── Test 11: All required columns removed ────────────────────────────────────

def test_all_required_columns_removed():
    """Multiple CRITICAL breaking changes accumulated → BLOCK with correct count."""
    decision = run_sentinel(BASE_EXPECTED, [])
    assert decision.decision == "BLOCK"
    # Empty → fail-closed, not individual column checks
    assert decision.is_fail_closed is True


def test_multiple_required_columns_removed():
    """Remove multiple required columns → BLOCK with multiple breaking changes."""
    incoming = [
        {"column_name": "card_last4", "data_type": "string", "is_nullable": True},
    ]
    decision = run_sentinel(BASE_EXPECTED, incoming)
    assert decision.decision == "BLOCK"
    assert len(decision.breaking_changes) >= 3  # at minimum: tx_id, amount, currency


# ─── Test 12: Primary key removed ─────────────────────────────────────────────

def test_primary_key_removal_blocks():
    """Remove transaction_id (PK) → BLOCK with PK_REMOVED."""
    incoming = [c for c in BASE_INCOMING if c["column_name"] != "transaction_id"]
    decision = run_sentinel(BASE_EXPECTED, incoming)
    assert decision.decision == "BLOCK"
    assert any(c.change_type == "PK_REMOVED" for c in decision.breaking_changes)


# ─── Test 13: Downstream consumer impact tracking ─────────────────────────────

def test_downstream_consumer_impact():
    """Removing 'amount' should report affected consumers that use it."""
    dep = SimpleNamespace(
        columns_used=["amount", "currency"],
        consumer_name="Daily Settlement Report",
    )
    incoming = [c for c in BASE_INCOMING if c["column_name"] != "amount"]
    decision = run_sentinel(BASE_EXPECTED, incoming, [dep])
    # The breaking change for 'amount' should list the consumer
    amount_change = next(
        (c for c in decision.breaking_changes if c.column_name == "amount"), None
    )
    assert amount_change is not None
    assert "Daily Settlement Report" in amount_change.affected_consumers
