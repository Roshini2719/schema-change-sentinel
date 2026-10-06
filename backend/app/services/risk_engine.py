from typing import List, Dict, Any
from ..models.models import SchemaChange, DownstreamDependency

class RiskEngine:
    """
    Mathematical Risk Engine for Schema Sentinel.
    
    Formula:
    RiskScore = min(100, Σ (SeverityWeight_c) + (PipelineHealthFactor) + Σ (DependencyCriticality_dep))
    
    Weights:
      Severity:
        CRITICAL: 40
        HIGH: 25
        MEDIUM: 10
        LOW: 2
        INFO: 0
        
      Pipeline Health:
        Rejection Ratio * 20 (0 to 20)
        
      Consumer Dependency Criticality:
        CRITICAL: 15
        HIGH: 10
        MEDIUM: 5
        LOW: 2
    """

    SEVERITY_WEIGHTS = {
        'CRITICAL': 40,
        'HIGH': 25,
        'MEDIUM': 10,
        'LOW': 2,
        'INFO': 0
    }

    DEPENDENCY_CRITICALITY_WEIGHTS = {
        'CRITICAL': 15,
        'HIGH': 10,
        'MEDIUM': 5,
        'LOW': 2
    }

    @classmethod
    def calculate_risk(
        cls,
        changes: List[SchemaChange],
        affected_dependencies: List[Dict[str, Any]],
        recent_rejection_rate: float = 0.0
    ) -> Dict[str, Any]:
        
        severity_score = 0
        has_critical = False
        breaking_count = 0

        for change in changes:
            sev = change.severity.upper() if change.severity else 'INFO'
            severity_score += cls.SEVERITY_WEIGHTS.get(sev, 0)
            if change.category == 'BREAKING' or sev == 'CRITICAL':
                has_critical = True
                breaking_count += 1

        pipeline_health_score = min(20.0, recent_rejection_rate * 20.0)

        dependency_score = 0
        for dep in affected_dependencies:
            crit = dep.get('criticality', 'MEDIUM').upper()
            dependency_score += cls.DEPENDENCY_CRITICALITY_WEIGHTS.get(crit, 5)

        raw_score = severity_score + pipeline_health_score + dependency_score
        final_risk_score = min(100.0, float(raw_score))

        # Gating logic
        if has_critical or final_risk_score >= 50.0:
            decision = 'BLOCK'
            reason = f'Unsafe publication blocked! Risk score {final_risk_score:.1f}/100 exceeds threshold (or critical breaking change present).'
        elif final_risk_score >= 20.0:
            decision = 'WARN'
            reason = f'Warning: Moderate schema risk detected ({final_risk_score:.1f}/100). Manual review recommended.'
        else:
            decision = 'ALLOW'
            reason = f'Schema validation passed safely. Risk score {final_risk_score:.1f}/100 is within acceptable limits.'

        return {
            'risk_score': round(final_risk_score, 1),
            'decision': decision,
            'reason': reason,
            'breakdown': {
                'severity_score': severity_score,
                'pipeline_health_score': round(pipeline_health_score, 1),
                'dependency_score': dependency_score,
                'breaking_changes_count': breaking_count,
                'affected_dependencies_count': len(affected_dependencies)
            }
        }
