from typing import Dict, Any, List

class ContractValidationResult(dict):
    @property
    def is_valid(self) -> bool:
        return self.get("valid", True)

def validate_contract(
    schema: Dict[str, Any],
    contract: Dict[str, Any]
) -> ContractValidationResult:
    valid = True
    violations = []
    
    schema_fields = schema.get("fields", {})
    
    # Process "rules" list if provided
    rules = contract.get("rules", [])
    for rule in rules:
        field_name = rule.get("field")
        expected_type = rule.get("type")
        is_required = rule.get("required", False)
        
        if is_required and field_name not in schema_fields:
            valid = False
            violations.append({
                "rule": "required",
                "field": field_name,
                "expected": "present",
                "actual": "missing",
                "severity": "CRITICAL"
            })
        elif field_name in schema_fields and expected_type:
            actual_type = schema_fields[field_name].get("type")
            if actual_type != expected_type:
                valid = False
                violations.append({
                    "rule": "type_mismatch",
                    "field": field_name,
                    "expected": expected_type,
                    "actual": actual_type,
                    "severity": "HIGH"
                })

    # Also handle map-based rules
    for req_field in contract.get("required_fields", []):
        if req_field not in schema_fields:
            valid = False
            violations.append({"rule": "required_fields", "field": req_field, "expected": "present", "actual": "missing", "severity": "CRITICAL"})
            
    for field, expected_type in contract.get("field_types", {}).items():
        if field in schema_fields:
            if schema_fields[field].get("type") != expected_type:
                valid = False
                violations.append({"rule": "field_types", "field": field, "expected": expected_type, "actual": schema_fields[field].get("type"), "severity": "HIGH"})
                
    for pk_field in contract.get("primary_keys", []):
        if pk_field in schema_fields and not schema_fields[pk_field].get("primary_key", False):
            valid = False
            violations.append({"rule": "primary_keys", "field": pk_field, "expected": "true", "actual": "false", "severity": "CRITICAL"})
            
    for non_null_field in contract.get("non_nullable_fields", []):
        if non_null_field in schema_fields and schema_fields[non_null_field].get("nullable", True):
            valid = False
            violations.append({"rule": "non_nullable_fields", "field": non_null_field, "expected": "false", "actual": "true", "severity": "HIGH"})
            
    for enum_field, expected_values in contract.get("enum_constraints", {}).items():
        if enum_field in schema_fields:
            actual_values = schema_fields[enum_field].get("values", [])
            if not set(expected_values).issubset(set(actual_values)):
                valid = False
                violations.append({"rule": "enum_constraints", "field": enum_field, "expected": str(expected_values), "actual": str(actual_values), "severity": "HIGH"})
                
    min_fields = contract.get("minimum_fields", 0)
    if len(schema_fields) < min_fields:
        valid = False
        violations.append({"rule": "minimum_fields", "field": "all", "expected": str(min_fields), "actual": str(len(schema_fields)), "severity": "MEDIUM"})
        
    return ContractValidationResult({
        "valid": valid,
        "violations": violations
    })
