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