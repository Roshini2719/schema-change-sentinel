from typing import Dict, Any, Optional, List
from app.services.schema_detector import detect_schema_changes
from app.services.contract_validator import validate_contract
from app.services.dependency_analyzer import analyze_dependencies
from app.services.pipeline_monitor import check_pipeline_health
from app.services.risk_engine import calculate_risk

def evaluate_publication(
    data_source_id: int,
    new_schema: Dict[str, Any],
    old_schema: Optional[Dict[str, Any]] = None,
    contract: Optional[Dict[str, Any]] = None,
    dependencies: Optional[List[Dict[str, Any]]] = None,
    pipeline_runs: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    
    if old_schema is None:
        return {
            "decision": "ALLOW",
            "risk_score": 0,
            "severity": "NONE",
            "changes": [],
            "contract_violations": [],
            "affected_dependencies": [],
            "pipeline_issues": [],
            "reasons": ["Initial schema registration allowed."]
        }
        
    try:
        schema_changes = detect_schema_changes(old_schema, new_schema)
        
        contract_result = None
        if contract:
            contract_result = validate_contract(new_schema, contract)
            
        dependency_result = None
        if dependencies:
            changed_fields = [c["field"] for c in schema_changes.get("changes", [])]
            dependency_result = analyze_dependencies(changed_fields, dependencies)
            
        pipeline_health = None
        if pipeline_runs:
            pipeline_health = check_pipeline_health(pipeline_runs)
            
        risk = calculate_risk(schema_changes, contract_result, dependency_result, pipeline_health)
        risk_score = risk.get("risk_score", 0)
        
        decision = "ALLOW"
        if risk_score >= 75:
            decision = "BLOCK"
        elif risk_score >= 50:
            decision = "WARN"
            
        return {
            "decision": decision,
            "risk_score": risk_score,
            "severity": risk.get("severity", "NONE"),
            "changes": schema_changes.get("changes", []),
            "contract_violations": contract_result.get("violations", []) if contract_result else [],
            "affected_dependencies": dependency_result.get("affected_dependencies", []) if dependency_result else [],
            "pipeline_issues": pipeline_health.get("issues", []) if pipeline_health else [],
            "reasons": risk.get("reasons", [])
        }
    except Exception as e:
        return {
            "decision": "BLOCK",
            "risk_score": 100,
            "severity": "CRITICAL",
            "changes": [],
            "contract_violations": [],
            "affected_dependencies": [],
            "pipeline_issues": [],
            "reasons": ["Publication blocked because schema safety could not be verified."]
        }
