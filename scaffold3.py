import os

PROJECT_ROOT = "/Users/muthamilroshini/.gemini/antigravity/scratch/schema-sentinel"

FILES = {}

FILES["backend/app/services/__init__.py"] = ""

FILES["backend/app/services/audit_service.py"] = """
from ..models.models import AuditLog

def log_action(db, organisation_id, user_id, user_email, action, resource_type=None, resource_id=None, details=None):
    audit_log = AuditLog(
        organisation_id=organisation_id,
        user_id=user_id,
        user_email=user_email,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log
""".strip()

FILES["backend/app/services/schema_sentinel.py"] = """
from typing import List, Dict, Any
from ..models.models import SchemaColumn, SchemaChange

def compare_schemas(expected_columns: List[SchemaColumn], incoming_columns: List[dict]) -> List[SchemaChange]:
    changes = []
    
    exp_dict = {col.column_name: col for col in expected_columns}
    inc_dict = {col['column_name']: col for col in incoming_columns}
    
    # 1, 3, 4, 6 - Check expected against incoming
    for name, exp_col in exp_dict.items():
        if name not in inc_dict:
            if exp_col.is_required:
                changes.append(SchemaChange(
                    change_type='COLUMN_REMOVED', column_name=name,
                    old_value=exp_col.data_type, new_value=None,
                    severity='CRITICAL', category='BREAKING',
                    reason='Required column was removed', recommendation='Restore column or coordinate change'
                ))
            elif exp_col.is_primary_key:
                changes.append(SchemaChange(
                    change_type='PK_REMOVED', column_name=name,
                    old_value=exp_col.data_type, new_value=None,
                    severity='CRITICAL', category='BREAKING',
                    reason='Primary key was removed', recommendation='Restore primary key'
                ))
            else:
                changes.append(SchemaChange(
                    change_type='COLUMN_REMOVED', column_name=name,
                    old_value=exp_col.data_type, new_value=None,
                    severity='MEDIUM', category='WARNING',
                    reason='Optional column was removed', recommendation='Ensure downstream is not affected'
                ))
        else:
            inc_col = inc_dict[name]
            
            if inc_col.get('data_type') != exp_col.data_type:
                # Basic compat check
                compatible = False
                if exp_col.data_type == 'decimal' and inc_col.get('data_type') == 'integer':
                    compatible = True # safe enough
                elif exp_col.data_type == 'string':
                    compatible = True # can cast most to string
                    
                if compatible:
                    changes.append(SchemaChange(
                        change_type='TYPE_CHANGED', column_name=name,
                        old_value=exp_col.data_type, new_value=inc_col.get('data_type'),
                        severity='MEDIUM', category='WARNING',
                        reason='Type changed but may be compatible', recommendation='Review compatibility'
                    ))
                else:
                    changes.append(SchemaChange(
                        change_type='TYPE_CHANGED', column_name=name,
                        old_value=exp_col.data_type, new_value=inc_col.get('data_type'),
                        severity='CRITICAL', category='BREAKING',
                        reason='Incompatible data type change', recommendation='Revert type change'
                    ))
                    
            if exp_col.is_required and not inc_col.get('is_required', True):
                changes.append(SchemaChange(
                    change_type='NULLABLE_CHANGED', column_name=name,
                    old_value='required', new_value='nullable',
                    severity='HIGH', category='BREAKING',
                    reason='Required field became nullable', recommendation='Make field required again'
                ))
                
            if exp_col.format_pattern and exp_col.format_pattern != inc_col.get('format_pattern'):
                changes.append(SchemaChange(
                    change_type='FORMAT_CHANGED', column_name=name,
                    old_value=exp_col.format_pattern, new_value=inc_col.get('format_pattern'),
                    severity='HIGH', category='BREAKING',
                    reason='Format pattern changed', recommendation='Match original format pattern'
                ))

    # 7, 8 Check for new columns
    for name, inc_col in inc_dict.items():
        if name not in exp_dict:
            if 'meta' in name.lower():
                changes.append(SchemaChange(
                    change_type='COLUMN_ADDED', column_name=name,
                    old_value=None, new_value=inc_col.get('data_type'),
                    severity='LOW', category='NON_BREAKING',
                    reason='New metadata column added', recommendation='None'
                ))
            else:
                changes.append(SchemaChange(
                    change_type='COLUMN_ADDED', column_name=name,
                    old_value=None, new_value=inc_col.get('data_type'),
                    severity='INFO', category='NON_BREAKING',
                    reason='New optional column added', recommendation='Update schema if expected'
                ))
                
    return changes

def has_breaking_changes(changes: List[SchemaChange]) -> bool:
    return any(c.category == 'BREAKING' for c in changes)

def get_changes_summary(changes: List[SchemaChange]) -> dict:
    summary = {'severity': {}, 'category': {}}
    for c in changes:
        summary['severity'][c.severity] = summary['severity'].get(c.severity, 0) + 1
        summary['category'][c.category] = summary['category'].get(c.category, 0) + 1
    return summary
""".strip()

FILES["backend/app/services/publication_gate.py"] = """
from typing import List
from ..models.models import SchemaChange, PublicationDecision
from .schema_sentinel import has_breaking_changes

def evaluate_publication(changes: List[SchemaChange], affected_deps: List) -> PublicationDecision:
    if has_breaking_changes(changes):
        return PublicationDecision(decision='BLOCK', reason='Breaking changes detected', breaking_changes=len([c for c in changes if c.category == 'BREAKING']), affected_dependencies=len(affected_deps))
    return PublicationDecision(decision='ALLOW', reason='No breaking changes', breaking_changes=0, affected_dependencies=len(affected_deps))

def process_override(db, pipeline_run_id, user_id, justification) -> PublicationDecision:
    decision = db.query(PublicationDecision).filter_by(pipeline_run_id=pipeline_run_id).first()
    if decision:
        decision.decision = 'OVERRIDE'
        decision.decided_by = user_id
        decision.override_justification = justification
        db.commit()
    return decision
""".strip()

FILES["backend/app/services/data_contract_validator.py"] = """
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
""".strip()

FILES["backend/app/services/dependency_analyzer.py"] = """
from typing import List
from ..models.models import SchemaChange, DownstreamDependency, DependencyColumn

def analyze_impact(db, organisation_id, changes: List[SchemaChange]) -> List[dict]:
    impacted = []
    change_cols = {c.column_name: c for c in changes}
    
    deps = db.query(DownstreamDependency).filter_by(organisation_id=organisation_id).all()
    for dep in deps:
        cols = db.query(DependencyColumn).filter_by(dependency_id=dep.id).all()
        affected_cols = [c for c in cols if c.column_name in change_cols]
        if affected_cols:
            critical_hits = [c for c in affected_cols if c.is_critical and change_cols[c.column_name].category == 'BREAKING']
            impact = 'HIGH' if critical_hits else 'LOW'
            impacted.append({
                'dependency_name': dep.name,
                'dependency_id': dep.id,
                'affected_columns': [c.column_name for c in affected_cols],
                'criticality': dep.criticality,
                'impact': impact
            })
    return impacted
""".strip()

FILES["backend/app/services/baseline_validator.py"] = """
from typing import List

def baseline_validate(incoming_columns: List[dict], record_count: int) -> dict:
    if record_count == 0:
        return {'valid': False, 'reason': '0 records received'}
    if not incoming_columns:
        return {'valid': False, 'reason': '0 columns received'}
    return {'valid': True, 'reason': 'Data looks okay'}
""".strip()

def main():
    for rel_path, content in FILES.items():
        full_path = os.path.join(PROJECT_ROOT, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
    print("Scaffold 3 complete.")

if __name__ == "__main__":
    main()
