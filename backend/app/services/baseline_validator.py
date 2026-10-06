from typing import List

def baseline_validate(incoming_columns: List[dict], record_count: int) -> dict:
    if record_count == 0:
        return {'valid': False, 'reason': '0 records received'}
    if not incoming_columns:
        return {'valid': False, 'reason': '0 columns received'}
    return {'valid': True, 'reason': 'Data looks okay'}