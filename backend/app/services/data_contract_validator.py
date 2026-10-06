from typing import List
import re
from ..models.models import ContractRule

def validate_against_contract(contract_rules: List[ContractRule], incoming_columns: List[dict], record_data: List[dict] = None) -> dict:
    violations = []
    inc_dict = {col['column_name']: col for col in incoming_columns}
    
    for rule in contract_rules:
        col = inc_dict.get(rule.column_name)
        if not col:
            if rule.is_required:
                violations.append({'rule': 'REQUIRED_FIELD', 'column': rule.column_name, 'reason': 'Missing required column in schema'})
            continue
            
        if col.get('data_type') != rule.data_type:
            violations.append({'rule': 'TYPE_MISMATCH', 'column': rule.column_name, 'reason': f'Expected {rule.data_type}, got {col.get("data_type")}'})
            
    if record_data:
        for i, record in enumerate(record_data):
            for rule in contract_rules:
                val = record.get(rule.column_name)
                if val is None:
                    if rule.is_required:
                        violations.append({'rule': 'NULL_VALUE', 'column': rule.column_name, 'reason': f'Null value in row {i}'})
                    continue
                
                if rule.min_value is not None and isinstance(val, (int, float)) and val < rule.min_value:
                    violations.append({'rule': 'MIN_VALUE', 'column': rule.column_name, 'reason': f'Value {val} < {rule.min_value} in row {i}'})
                    
                if rule.max_value is not None and isinstance(val, (int, float)) and val > rule.max_value:
                    violations.append({'rule': 'MAX_VALUE', 'column': rule.column_name, 'reason': f'Value {val} > {rule.max_value} in row {i}'})
                    
                if rule.allowed_values:
                    try:
                        import json
                        allowed = json.loads(rule.allowed_values)
                        if val not in allowed:
                            violations.append({'rule': 'ALLOWED_VALUES', 'column': rule.column_name, 'reason': f'Value {val} not allowed in row {i}'})
                    except:
                        pass
                        
                if rule.regex_pattern and isinstance(val, str):
                    if not re.match(rule.regex_pattern, val):
                        violations.append({'rule': 'REGEX', 'column': rule.column_name, 'reason': f'Value {val} failed regex match in row {i}'})

    return {'valid': len(violations) == 0, 'violations': violations}