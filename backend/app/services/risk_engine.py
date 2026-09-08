from typing import Dict, Any, Optional

def calculate_risk(
    schema_changes: Dict[str, Any],
    contract_result: Optional[Dict[str, Any]] = None,
    dependency_result: Optional[Dict[str, Any]] = None,
    pipeline_health: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    
    base_scores = {"CRITICAL": 100, "HIGH": 75, "MEDIUM": 50, "LOW": 25, "NONE": 0}
    severity = schema_changes.get("severity", "NONE")
    base_score = base_scores.get(severity, 0)
    
    fin_esc = 0
    dep_esc = 0
    pipe_esc = 0
    contract_esc = 0
    reasons = []
    
    for change in schema_changes.get("changes", []):
        reasons.append(change.get("reason", "Unknown change"))
            
    if dependency_result and dependency_result.get("total_affected", 0) > 0:
        if dependency_result.get("has_critical"):
            dep_esc += 20
            reasons.append("Critical downstream dependency affected")
        else:
            dep_esc += 10
            reasons.append("Downstream dependency affected")
            
        extra = dependency_result.get("total_affected", 0) - 1
        if extra > 0:
            dep_esc += (extra * 5)
            
    if pipeline_health and not pipeline_health.get("healthy", True):
        pipe_esc += 15
        reasons.append("Pipeline health issues detected")
        
    if contract_result and not contract_result.get("valid", True):
        contract_esc += 10
        reasons.append("Contract violations detected")
        
    total_score = base_score + fin_esc + dep_esc + pipe_esc + contract_esc
    total_score = min(total_score, 100)
    
    final_severity = "NONE"
    if total_score >= 100:
        final_severity = "CRITICAL"
    elif total_score >= 75:
        final_severity = "HIGH"
    elif total_score >= 50:
        final_severity = "MEDIUM"
    elif total_score >= 25:
        final_severity = "LOW"
        
    return {
        "risk_score": total_score,
        "severity": final_severity,
        "reasons": reasons,
        "breakdown": {
            "base_score": base_score,
            "financial_escalation": fin_esc,
            "dependency_escalation": dep_esc,
            "pipeline_escalation": pipe_esc,
            "contract_escalation": contract_esc
        }
    }
