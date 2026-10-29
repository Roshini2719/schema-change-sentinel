from typing import List, Dict, Any, Optional, Union
from ..models.models import SchemaChange, DownstreamDependency

class RiskScoreResult(float):
    def __new__(cls, val, data=None):
        instance = super().__new__(cls, val)
        instance.data = data or {}
        return instance

    def __getitem__(self, item):
        return self.data[item]

    def get(self, item, default=None):
        return self.data.get(item, default)

    def __contains__(self, item):
        return item in self.data

class RiskEngine:
    """
    Mathematical Risk Engine for Schema Sentinel.
    
    Formula:
    RiskScore = min(100, Σ (SeverityWeight_c) + (PipelineHealthFactor) + Σ (DependencyCriticality_dep))
    """

    SEVERITY_WEIGHTS = {
        'CRITICAL': 100,
        'HIGH': 75,
        'MEDIUM': 50,
        'LOW': 25,
        'INFO': 0,
        'NONE': 0
    }

    DEPENDENCY_CRITICALITY_WEIGHTS = {
        'CRITICAL': 20,
        'HIGH': 15,
        'MEDIUM': 10,
        'LOW': 5
    }

    @classmethod
    def calculate_risk(
        cls,
        changes: Union[List[Any], Dict[str, Any]],
        affected_dependencies: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
        recent_rejection_rate: float = 0.0,
        pipeline_health: Optional[Dict[str, Any]] = None
    ) -> RiskScoreResult:
        if affected_dependencies is None:
            affected_dependencies = []

        # If changes is empty
        if not changes:
            return RiskScoreResult(0.0, {
                'risk_score': 0.0,
                'decision': 'ALLOW',
                'reason': 'No changes detected',
                'severity': 'NONE'
            })

        # Handle list vs dict of changes
        change_list = changes.get("changes", []) if isinstance(changes, dict) else changes
        if not change_list:
            sev = changes.get("severity", "NONE") if isinstance(changes, dict) else "NONE"
            score = cls.SEVERITY_WEIGHTS.get(sev, 0)
            return RiskScoreResult(float(score), {
                'risk_score': float(score),
                'decision': 'BLOCK' if score >= 75 else 'ALLOW',
                'severity': sev
            })

        severity_score = 0
        has_critical = False
        breaking_count = 0

        for change in change_list:
            if isinstance(change, dict):
                sev = change.get("severity", "INFO").upper()
                is_brk = change.get("breaking", False) or sev in ("CRITICAL", "HIGH")
            else:
                sev = getattr(change, "severity", "INFO").upper() if getattr(change, "severity", None) else 'INFO'
                is_brk = getattr(change, "category", "") == 'BREAKING' or sev in ("CRITICAL", "HIGH")

            if sev == 'CRITICAL':
                has_critical = True
                breaking_count += 1
                severity_score = max(severity_score, 100)
            elif sev == 'HIGH':
                breaking_count += 1
                severity_score = max(severity_score, 75)
            elif sev == 'MEDIUM':
                severity_score = max(severity_score, 50)
            elif sev == 'LOW':
                severity_score = max(severity_score, 25)

        pipeline_health_score = min(20.0, recent_rejection_rate * 20.0)

        dep_list = affected_dependencies.get("affected_dependencies", []) if isinstance(affected_dependencies, dict) else affected_dependencies
        dependency_score = 0
        for dep in dep_list:
            crit = dep.get('criticality', 'MEDIUM').upper()
            dependency_score += cls.DEPENDENCY_CRITICALITY_WEIGHTS.get(crit, 5)

        raw_score = max(severity_score, min(100.0, float(severity_score + pipeline_health_score + dependency_score)))
        final_risk_score = min(100.0, float(raw_score))

        # Gating logic
        if has_critical or final_risk_score >= 75.0:
            decision = 'BLOCK'
            reason = f'Unsafe publication blocked! Risk score {final_risk_score:.1f}/100 exceeds threshold.'
        elif final_risk_score >= 25.0:
            decision = 'WARN'
            reason = f'Warning: Moderate schema risk detected ({final_risk_score:.1f}/100).'
        else:
            decision = 'ALLOW'
            reason = f'Schema validation passed safely ({final_risk_score:.1f}/100).'

        return RiskScoreResult(round(final_risk_score, 1), {
            'risk_score': round(final_risk_score, 1),
            'decision': decision,
            'reason': reason,
            'severity': 'CRITICAL' if has_critical else ('HIGH' if final_risk_score >= 75 else 'LOW'),
            'breakdown': {
                'severity_score': severity_score,
                'pipeline_health_score': round(pipeline_health_score, 1),
                'dependency_score': dependency_score,
                'breaking_changes_count': breaking_count,
                'affected_dependencies_count': len(dep_list)
            }
        })

calculate_risk = RiskEngine.calculate_risk
