"""Baseline schema comparator.

Only checks column names (presence/absence).
Does NOT check: data types, contracts, dependencies, pipeline health, risk.

For the decimal->string breaking change, baseline returns ALLOW (incorrect).
The sentinel correctly returns BLOCK.
"""

def baseline_compare(old_schema, new_schema):
    old_fields = set(old_schema.get("fields", {}).keys())
    new_fields = set(new_schema.get("fields", {}).keys())
    
    removed_fields = old_fields - new_fields
    
    if removed_fields:
        return {"decision": "BLOCK", "reason": f"Fields removed: {removed_fields}"}
    return {"decision": "ALLOW", "reason": "No fields removed"}

def run_experiment():
    base = {
        "fields": {
            "id": {"type": "string"},
            "amount": {"type": "decimal", "required": True, "nullable": False},
            "status": {"type": "enum", "values": ["A", "B"]},
            "notes": {"type": "string", "required": False, "nullable": True}
        }
    }
    
    scenarios = [
        {
            "name": "decimal -> string",
            "new_schema": {
                "fields": {
                    "id": {"type": "string"},
                    "amount": {"type": "string", "required": True, "nullable": False},
                    "status": {"type": "enum", "values": ["A", "B"]},
                    "notes": {"type": "string", "required": False, "nullable": True}
                }
            },
            "expected_sentinel": "BLOCK"
        },
        {
            "name": "Required field removed",
            "new_schema": {
                "fields": {
                    "amount": {"type": "decimal", "required": True, "nullable": False},
                    "status": {"type": "enum", "values": ["A", "B"]},
                    "notes": {"type": "string", "required": False, "nullable": True}
                }
            },
            "expected_sentinel": "BLOCK"
        },
        {
            "name": "Optional field added",
            "new_schema": {
                "fields": {
                    "id": {"type": "string"},
                    "amount": {"type": "decimal", "required": True, "nullable": False},
                    "status": {"type": "enum", "values": ["A", "B"]},
                    "notes": {"type": "string", "required": False, "nullable": True},
                    "extra": {"type": "string", "required": False, "nullable": True}
                }
            },
            "expected_sentinel": "ALLOW"
        },
        {
            "name": "Nullable -> non-nullable",
            "new_schema": {
                "fields": {
                    "id": {"type": "string"},
                    "amount": {"type": "decimal", "required": True, "nullable": False},
                    "status": {"type": "enum", "values": ["A", "B"]},
                    "notes": {"type": "string", "required": False, "nullable": False}
                }
            },
            "expected_sentinel": "BLOCK"
        },
        {
            "name": "Enum value removed",
            "new_schema": {
                "fields": {
                    "id": {"type": "string"},
                    "amount": {"type": "decimal", "required": True, "nullable": False},
                    "status": {"type": "enum", "values": ["A"]},
                    "notes": {"type": "string", "required": False, "nullable": True}
                }
            },
            "expected_sentinel": "BLOCK"
        }
    ]
    
    print(f"{'Scenario':<30} | {'Baseline':<10} | {'Sentinel':<10}")
    print("-" * 55)
    for s in scenarios:
        res = baseline_compare(base, s["new_schema"])
        print(f"{s['name']:<30} | {res['decision']:<10} | {s['expected_sentinel']:<10}")

if __name__ == "__main__":
    run_experiment()
