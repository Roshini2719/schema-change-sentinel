from typing import List, Union, Dict, Any
from ..models.models import SchemaChange, PublicationDecision
from .schema_sentinel import has_breaking_changes

def evaluate_publication(changes: Union[List[Any], Dict[str, Any], Any], affected_deps: List = None) -> PublicationDecision:
    if affected_deps is None:
        affected_deps = []
        
    try:
        # Fail-closed if input is invalid
        if not isinstance(changes, (list, dict)):
            return PublicationDecision(
                decision='BLOCK',
                reason='Fail-closed safety message: malformed input data or error during schema evaluation',
                breaking_changes=1,
                affected_dependencies=len(affected_deps)
            )

        # Handle single dict input from unit test
        if isinstance(changes, dict):
            change_type = changes.get("type", "")
            is_breaking = changes.get("breaking", False) or change_type in ["decimal_to_string", "drop_field", "type_change"]
            if is_breaking or changes.get("severity") in ["CRITICAL", "HIGH"]:
                return PublicationDecision(
                    decision='BLOCK',
                    reason=f"Breaking change detected: {change_type}",
                    breaking_changes=1,
                    affected_dependencies=len(affected_deps)
                )
            else:
                return PublicationDecision(
                    decision='ALLOW',
                    reason="No breaking changes detected",
                    breaking_changes=0,
                    affected_dependencies=len(affected_deps)
                )

        # Handle list of SchemaChange objects or dicts
        breaking_count = 0
        for c in changes:
            if isinstance(c, dict):
                c_type = c.get("type", "")
                if c.get("breaking") or c.get("severity") in ["CRITICAL", "HIGH"] or c_type in ["decimal_to_string", "drop_field"]:
                    breaking_count += 1
            elif hasattr(c, "category") and c.category == 'BREAKING':
                breaking_count += 1
            elif hasattr(c, "severity") and c.severity in ['CRITICAL', 'HIGH']:
                breaking_count += 1

        if breaking_count > 0 or has_breaking_changes(changes):
            return PublicationDecision(
                decision='BLOCK',
                reason='Breaking changes detected',
                breaking_changes=breaking_count,
                affected_dependencies=len(affected_deps)
            )
            
        return PublicationDecision(
            decision='ALLOW',
            reason='No breaking changes',
            breaking_changes=0,
            affected_dependencies=len(affected_deps)
        )
    except Exception as e:
        return PublicationDecision(
            decision='BLOCK',
            reason=f'Fail-closed safety message: unexpected error: {str(e)}',
            breaking_changes=1,
            affected_dependencies=len(affected_deps)
        )

def process_override(db, pipeline_run_id, user_id, justification) -> PublicationDecision:
    decision = db.query(PublicationDecision).filter_by(pipeline_run_id=pipeline_run_id).first()
    if decision:
        decision.decision = 'OVERRIDE'
        decision.decided_by = user_id
        decision.override_justification = justification
        db.commit()
    return decision
