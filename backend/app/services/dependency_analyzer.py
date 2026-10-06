from typing import List
from ..models.models import SchemaChange, DownstreamDependency, DependencyColumn

def analyze_impact(db, organisation_id, changes: List[SchemaChange]) -> List[dict]:
    impacted = []
    change_cols = {c.column_name: c for c in changes}
    
    deps = db.query(DownstreamDependency).filter_by(organisation_id=organisation_id).all()
    for dep in deps:
        cols = db.query(DependencyColumn).filter_by(dependency_id=dep.id).all()
        affected_cols = [c for c in cols if c.column_name in change_cols]
        if affected_cols:
            critical_hits = [c for c in affected_cols if c.is_critical and change_cols[c.column_name].category == 'BREAKING']
            impact = 'HIGH' if critical_hits else 'LOW'
            impacted.append({
                'dependency_name': dep.name,
                'dependency_id': dep.id,
                'affected_columns': [c.column_name for c in affected_cols],
                'criticality': dep.criticality,
                'impact': impact
            })
    return impacted