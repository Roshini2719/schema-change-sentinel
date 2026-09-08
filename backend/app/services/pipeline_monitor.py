from typing import Dict, Any, List, Optional

def check_pipeline_health(
    pipeline_runs: List[Dict[str, Any]],
    thresholds: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    if thresholds is None:
        thresholds = {
            "zero_records": True,
            "drop_threshold": 0.3,
            "rejection_rate": 0.1,
            "require_schema_match": True
        }
        
    healthy = True
    issues = []
    max_severity = "NONE"
    
    def update_severity(sev):
        nonlocal max_severity
        levels = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        if levels.get(sev, 0) > levels.get(max_severity, 0):
            max_severity = sev
            
    run_ids = set()
            
    for run in pipeline_runs:
        run_id = run.get("run_id")
        if run_id in run_ids:
            healthy = False
            issues.append({"type": "DUPLICATE_RUN_ID", "severity": "HIGH", "description": f"Duplicate run_id: {run_id}"})
            update_severity("HIGH")
        run_ids.add(run_id)
        
        expected = run.get("expected_records")
        received = run.get("records_received", 0)
        processed = run.get("records_processed", 0)
        rejected = run.get("records_rejected", 0)
        
        if thresholds.get("zero_records") and received == 0:
            healthy = False
            issues.append({"type": "ZERO_RECORDS", "severity": "CRITICAL", "description": f"Zero records received for run {run_id}"})
            update_severity("CRITICAL")
            
        if expected and received:
            drop = (expected - received) / expected
            if drop > thresholds.get("drop_threshold", 0.3):
                healthy = False
                issues.append({"type": "LARGE_RECORD_DROP", "severity": "HIGH", "description": f"Large record drop for run {run_id}: {drop:.1%} drop"})
                update_severity("HIGH")
                
        if received > 0:
            rej_rate = rejected / received
            if rej_rate > thresholds.get("rejection_rate", 0.1):
                healthy = False
                issues.append({"type": "HIGH_REJECTION_RATE", "severity": "HIGH", "description": f"High rejection rate for run {run_id}: {rej_rate:.1%}"})
                update_severity("HIGH")
                
        if received > (processed + rejected):
            healthy = False
            issues.append({"type": "INCOMPLETE_PROCESSING", "severity": "MEDIUM", "description": f"Incomplete processing for run {run_id}"})
            update_severity("MEDIUM")
            
    return {
        "healthy": healthy,
        "issues": issues,
        "severity": max_severity
    }
