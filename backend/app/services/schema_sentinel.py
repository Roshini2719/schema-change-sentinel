"""
Schema Sentinel Engine
======================
Core comparison logic. Compares an incoming schema against a registered contract schema.
Returns a list of change events classified as BREAKING, WARNING, or INFO.
Publish gate: any BREAKING change → BLOCK.
Fail-closed: any exception during validation → BLOCK with ERROR status.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# ─── Type compatibility matrix ────────────────────────────────────────────────

# (from_type, to_type) -> True if backward compatible (no data loss)
COMPATIBLE_TYPE_CHANGES: Dict[Tuple[str, str], bool] = {
    ("integer", "decimal"): True,    # widening
    ("integer", "string"): False,    # string ops break arithmetic
    ("decimal", "string"): False,
    ("boolean", "string"): False,
    ("date", "datetime"): True,      # widening
    ("datetime", "date"): False,     # truncation = data loss
    ("string", "integer"): False,
    ("string", "decimal"): False,
    ("decimal", "integer"): False,   # precision loss
}

def types_compatible(from_type: str, to_type: str) -> bool:
    if from_type == to_type:
        return True
    key = (from_type.lower(), to_type.lower())
    return COMPATIBLE_TYPE_CHANGES.get(key, False)


# ─── Data classes ─────────────────────────────────────────────────────────────

class ChangeCategory(str, Enum):
    BREAKING = "BREAKING"
    WARNING = "WARNING"
    INFO = "INFO"
    ERROR = "ERROR"

class ChangeSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

@dataclass
class SchemaChangeEvent:
    change_type: str
    column_name: str
    old_value: Optional[str]
    new_value: Optional[str]
    severity: str
    category: str
    reason: str
    recommendation: str
    affected_consumers: List[str] = field(default_factory=list)

@dataclass
class GateDecision:
    decision: str           # ALLOW | BLOCK | ERROR
    reason: str
    breaking_changes: List[SchemaChangeEvent]
    warning_changes: List[SchemaChangeEvent]
    info_changes: List[SchemaChangeEvent]
    affected_consumers: List[str]
    is_fail_closed: bool = False

    @property
    def all_changes(self) -> List[SchemaChangeEvent]:
        return self.breaking_changes + self.warning_changes + self.info_changes


# ─── Main comparison function ──────────────────────────────────────────────────

def compare_schemas(
    expected_columns: List[Any],          # list of SchemaColumn ORM objects
    incoming_columns: List[Dict[str, Any]],  # list of dicts from incoming data
    dependencies: Optional[List[Any]] = None  # list of DownstreamDependency ORM objects
) -> List[SchemaChangeEvent]:
    """
    Compare registered schema against incoming schema.
    Returns all detected SchemaChangeEvents (BREAKING, WARNING, INFO).
    """
    changes: List[SchemaChangeEvent] = []
    deps = dependencies or []

    # ── Validate incoming structure ──────────────────────────────────────────
    if not isinstance(incoming_columns, list):
        raise ValueError("incoming_columns must be a list of dicts")

    seen_names = set()
    for col in incoming_columns:
        name = col.get("column_name", "")
        if name in seen_names:
            changes.append(SchemaChangeEvent(
                change_type="DUPLICATE_COLUMN",
                column_name=name,
                old_value=None,
                new_value=None,
                severity=ChangeSeverity.HIGH.value,
                category=ChangeCategory.BREAKING.value,
                reason=f"Duplicate column name '{name}' in incoming schema",
                recommendation="Deduplicate column names in partner schema",
            ))
        seen_names.add(name)

    exp_dict = {col.column_name: col for col in expected_columns}
    inc_dict = {col["column_name"]: col for col in incoming_columns if "column_name" in col}

    # ── Check expected columns against incoming ──────────────────────────────
    for name, exp_col in exp_dict.items():
        if name not in inc_dict:
            # Column is missing from incoming payload
            affected = _consumers_using_column(name, deps)
            if exp_col.is_primary_key:
                changes.append(SchemaChangeEvent(
                    change_type="PK_REMOVED",
                    column_name=name,
                    old_value=exp_col.data_type,
                    new_value=None,
                    severity=ChangeSeverity.CRITICAL.value,
                    category=ChangeCategory.BREAKING.value,
                    reason=f"Primary key column '{name}' was removed",
                    recommendation="Restore the primary key or negotiate a schema migration",
                    affected_consumers=affected,
                ))
            elif exp_col.is_required:
                changes.append(SchemaChangeEvent(
                    change_type="COLUMN_REMOVED",
                    column_name=name,
                    old_value=exp_col.data_type,
                    new_value=None,
                    severity=ChangeSeverity.CRITICAL.value,
                    category=ChangeCategory.BREAKING.value,
                    reason=f"Required column '{name}' was removed",
                    recommendation="Restore column or coordinate with partner to version the schema",
                    affected_consumers=affected,
                ))
            else:
                changes.append(SchemaChangeEvent(
                    change_type="COLUMN_REMOVED",
                    column_name=name,
                    old_value=exp_col.data_type,
                    new_value=None,
                    severity=ChangeSeverity.MEDIUM.value,
                    category=ChangeCategory.WARNING.value,
                    reason=f"Optional column '{name}' was removed",
                    recommendation="Verify downstream consumers do not rely on this column",
                    affected_consumers=affected,
                ))
        else:
            inc_col = inc_dict[name]

            # Type change check
            inc_type = (inc_col.get("data_type") or "").lower().strip()
            exp_type = (exp_col.data_type or "").lower().strip()
            if inc_type and inc_type != exp_type:
                affected = _consumers_using_column(name, deps)
                if types_compatible(exp_type, inc_type):
                    changes.append(SchemaChangeEvent(
                        change_type="TYPE_CHANGED",
                        column_name=name,
                        old_value=exp_type,
                        new_value=inc_type,
                        severity=ChangeSeverity.LOW.value,
                        category=ChangeCategory.INFO.value,
                        reason=f"Type widening: '{name}' changed from {exp_type} to {inc_type} (compatible)",
                        recommendation="Monitor downstream for unexpected behaviour",
                        affected_consumers=affected,
                    ))
                else:
                    changes.append(SchemaChangeEvent(
                        change_type="TYPE_CHANGED",
                        column_name=name,
                        old_value=exp_type,
                        new_value=inc_type,
                        severity=ChangeSeverity.CRITICAL.value,
                        category=ChangeCategory.BREAKING.value,
                        reason=f"Incompatible type change: '{name}' changed from {exp_type} to {inc_type}",
                        recommendation="Revert type change or publish a new schema version",
                        affected_consumers=affected,
                    ))

            # Nullability change check
            inc_nullable = inc_col.get("is_nullable", None)
            if inc_nullable is not None and not exp_col.is_nullable and bool(inc_nullable):
                affected = _consumers_using_column(name, deps)
                changes.append(SchemaChangeEvent(
                    change_type="NULLABLE_CHANGED",
                    column_name=name,
                    old_value="NOT NULL",
                    new_value="NULLABLE",
                    severity=ChangeSeverity.HIGH.value,
                    category=ChangeCategory.BREAKING.value,
                    reason=f"Required field '{name}' became nullable — downstream NOT NULL constraints will break",
                    recommendation="Enforce NOT NULL in partner contract or reject the change",
                    affected_consumers=affected,
                ))

    # ── Check incoming for new columns ───────────────────────────────────────
    for name, inc_col in inc_dict.items():
        if name not in exp_dict:
            changes.append(SchemaChangeEvent(
                change_type="COLUMN_ADDED",
                column_name=name,
                old_value=None,
                new_value=inc_col.get("data_type"),
                severity=ChangeSeverity.INFO.value,
                category=ChangeCategory.INFO.value,
                reason=f"New column '{name}' added — non-breaking addition",
                recommendation="Register the new column in the data contract if it should be required",
            ))

    return changes


def make_gate_decision(
    changes: List[SchemaChangeEvent],
    dependencies: Optional[List[Any]] = None
) -> GateDecision:
    """
    Given a list of schema change events, decide whether to ALLOW or BLOCK publication.
    Any BREAKING change → BLOCK.
    """
    breaking = [c for c in changes if c.category == ChangeCategory.BREAKING.value]
    warnings = [c for c in changes if c.category == ChangeCategory.WARNING.value]
    infos = [c for c in changes if c.category == ChangeCategory.INFO.value]

    all_affected: List[str] = []
    for c in breaking + warnings:
        all_affected.extend(c.affected_consumers)
    all_affected = list(set(all_affected))

    if breaking:
        reason = f"{len(breaking)} breaking change(s) detected: " + ", ".join(
            f"{c.change_type} on '{c.column_name}'" for c in breaking
        )
        return GateDecision(
            decision="BLOCK",
            reason=reason,
            breaking_changes=breaking,
            warning_changes=warnings,
            info_changes=infos,
            affected_consumers=all_affected,
        )

    return GateDecision(
        decision="ALLOW",
        reason="No breaking changes detected",
        breaking_changes=[],
        warning_changes=warnings,
        info_changes=infos,
        affected_consumers=all_affected,
    )


def run_sentinel(
    expected_columns: List[Any],
    incoming_columns: List[Dict[str, Any]],
    dependencies: Optional[List[Any]] = None
) -> GateDecision:
    """
    Fail-closed entry point.
    Any internal exception → BLOCK with ERROR category.
    """
    try:
        if not incoming_columns:
            return GateDecision(
                decision="BLOCK",
                reason="Incoming schema is empty or could not be parsed",
                breaking_changes=[SchemaChangeEvent(
                    change_type="SCHEMA_PARSE_ERROR",
                    column_name="*",
                    old_value=None,
                    new_value=None,
                    severity=ChangeSeverity.CRITICAL.value,
                    category=ChangeCategory.ERROR.value,
                    reason="Incoming schema payload was empty or malformed",
                    recommendation="Ensure partner sends a valid schema payload",
                )],
                warning_changes=[],
                info_changes=[],
                affected_consumers=[],
                is_fail_closed=True,
            )

        changes = compare_schemas(expected_columns, incoming_columns, dependencies)
        return make_gate_decision(changes, dependencies)

    except Exception as exc:
        logger.exception("Schema sentinel internal error — failing closed: %s", exc)
        return GateDecision(
            decision="BLOCK",
            reason=f"Internal validation error (fail-closed): {str(exc)}",
            breaking_changes=[SchemaChangeEvent(
                change_type="INTERNAL_ERROR",
                column_name="*",
                old_value=None,
                new_value=None,
                severity=ChangeSeverity.CRITICAL.value,
                category=ChangeCategory.ERROR.value,
                reason=f"Sentinel engine raised an exception: {str(exc)}",
                recommendation="Investigate sentinel logs and fix the validation pipeline",
            )],
            warning_changes=[],
            info_changes=[],
            affected_consumers=[],
            is_fail_closed=True,
        )


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _consumers_using_column(column_name: str, dependencies: List[Any]) -> List[str]:
    """Return consumer names that reference the given column."""
    result = []
    for dep in dependencies:
        cols_used = dep.columns_used or []
        if column_name in cols_used:
            result.append(dep.consumer_name)
    return result

def has_breaking_changes(changes: List[Any]) -> bool:
    if not changes:
        return False
    for c in changes:
        if hasattr(c, "category") and str(c.category).upper() in ("BREAKING", "CHANGECATEGORY.BREAKING"):
            return True
        if hasattr(c, "severity") and c.severity in ("CRITICAL", "HIGH"):
            return True
        if isinstance(c, dict) and (c.get("breaking") or c.get("severity") in ("CRITICAL", "HIGH")):
            return True
    return False

def get_changes_summary(changes: List[Any]) -> dict:
    breaking = [c for c in changes if (hasattr(c, "severity") and c.severity in ("CRITICAL", "HIGH")) or (isinstance(c, dict) and c.get("severity") in ("CRITICAL", "HIGH"))]
    return {
        "total_changes": len(changes),
        "breaking_changes": len(breaking),
        "has_breaking": len(breaking) > 0
    }
