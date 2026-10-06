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