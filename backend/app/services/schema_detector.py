from typing import Optional, Dict, Any, List, Set

FINANCIAL_FIELDS = {"amount", "price", "balance", "total", "fee", "cost", "rate", "interest", "payment", "credit", "debit"}

def detect_schema_changes(
    old_schema: Dict[str, Any],
    new_schema: Dict[str, Any],
    downstream_fields: Optional[Set[str]] = None
) -> Dict[str, Any]:
    if downstream_fields is None:
        downstream_fields = set()
        
    old_fields = old_schema.get("fields", {})
    new_fields = new_schema.get("fields", {})
    
    changes = []
    breaking = False
    max_severity = "NONE"
    
    def update_severity(sev: str):
        nonlocal max_severity
        levels = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        if levels.get(sev, 0) > levels.get(max_severity, 0):
            max_severity = sev
            
    def is_financial(field_name: str) -> bool:
        field_name_lower = field_name.lower()
        return any(term in field_name_lower for term in FINANCIAL_FIELDS)
        
    def check_type_change(old_type: str, new_type: str) -> bool:
        # returns True if incompatible
        widenings = {("int", "decimal"), ("int", "float"), ("float", "decimal")}
        if old_type == new_type:
            return False
        if (old_type, new_type) in widenings:
            return False
        return True

    for field_name, old_field in old_fields.items():
        if field_name not in new_fields:
            if old_field.get("required", True):
                changes.append({
                    "field": field_name,
                    "change_type": "REQUIRED_FIELD_REMOVED",
                    "severity": "CRITICAL",
                    "reason": f"Required field '{field_name}' was removed."
                })
                breaking = True
                update_severity("CRITICAL")
            elif field_name in downstream_fields:
                changes.append({
                    "field": field_name,
                    "change_type": "DOWNSTREAM_FIELD_REMOVED",
                    "severity": "HIGH",
                    "reason": f"Field '{field_name}' used downstream was removed."
                })
                breaking = True
                update_severity("HIGH")
            else:
                changes.append({
                    "field": field_name,
                    "change_type": "OPTIONAL_FIELD_REMOVED",
                    "severity": "MEDIUM",
                    "reason": f"Optional field '{field_name}' was removed."
                })
                update_severity("MEDIUM")
            continue
            
        new_field = new_fields[field_name]
        
        # primary key removed
        if old_field.get("primary_key", False) and not new_field.get("primary_key", False):
            changes.append({
                "field": field_name,
                "change_type": "PRIMARY_KEY_REMOVED",
                "severity": "CRITICAL",
                "reason": f"Primary key constraint removed from '{field_name}'."
            })
            breaking = True
            update_severity("CRITICAL")
            
        # nullability changed
        if old_field.get("nullable", False) and not new_field.get("nullable", False):
            changes.append({
                "field": field_name,
                "change_type": "NULLABLE_TO_NON_NULLABLE",
                "severity": "HIGH",
                "reason": f"Field '{field_name}' changed from nullable to non-nullable."
            })
            breaking = True
            update_severity("HIGH")
            
        # type changes
        old_type = old_field.get("type", "string")
        new_type = new_field.get("type", "string")
        if check_type_change(old_type, new_type):
            change_type = "INCOMPATIBLE_TYPE_CHANGE"
            severity = "HIGH"
            
            if is_financial(field_name):
                severity = "CRITICAL"
                
            changes.append({
                "field": field_name,
                "change_type": change_type,
                "severity": severity,
                "reason": f"Type changed from {old_type} to {new_type}.",
                "old_type": old_type,
                "new_type": new_type
            })
            breaking = True
            update_severity(severity)
            
        # enum values
        old_values = old_field.get("values")
        new_values = new_field.get("values")
        if isinstance(old_values, list) and isinstance(new_values, list):
            removed = set(old_values) - set(new_values)
            if removed:
                changes.append({
                    "field": field_name,
                    "change_type": "ENUM_VALUE_REMOVED",
                    "severity": "HIGH",
                    "reason": f"Enum values removed: {', '.join(removed)}"
                })
                breaking = True
                update_severity("HIGH")

    for field_name, new_field in new_fields.items():
        if field_name not in old_fields:
            if new_field.get("required", True) and not new_field.get("default_value"):
                changes.append({
                    "field": field_name,
                    "change_type": "REQUIRED_FIELD_ADDED",
                    "severity": "HIGH",
                    "reason": f"Required field '{field_name}' added without default value."
                })
                breaking = True
                update_severity("HIGH")
            else:
                changes.append({
                    "field": field_name,
                    "change_type": "FIELD_ADDED",
                    "severity": "LOW",
                    "reason": f"New field '{field_name}' added."
                })
                update_severity("LOW")
                
    risk_score = {"NONE": 0, "LOW": 25, "MEDIUM": 50, "HIGH": 75, "CRITICAL": 100}[max_severity]
    
    return {
        "breaking": breaking,
        "severity": max_severity,
        "risk_score": risk_score,
        "changes": changes
    }
