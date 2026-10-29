import re
from typing import List, Dict, Any, Set, Union
from ..models.models import SchemaChange, DownstreamDependency, DependencyColumn

SQL_KEYWORDS = {
    "select", "from", "where", "and", "or", "not", "in", "is", "null", "group", "by",
    "order", "having", "limit", "offset", "join", "left", "right", "inner", "outer",
    "full", "cross", "on", "as", "sum", "avg", "count", "min", "max", "distinct",
    "case", "when", "then", "else", "end", "like", "ilike", "between", "union", "all",
}

def extract_fields(query: str) -> Set[str]:
    """Extract field names from a SQL query string."""
    tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', query)
    fields = set()
    from_match = re.search(r'\bfrom\s+([a-zA-Z0-9_]+)', query, re.IGNORECASE)
    table_name = from_match.group(1).lower() if from_match else None

    for token in tokens:
        low = token.lower()
        if low not in SQL_KEYWORDS and low != table_name:
            fields.add(token)
    return fields

def analyze_dependencies(changed_fields: List[str], dependencies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze which dependencies are affected by changed fields."""
    affected = []
    changed_set = set(changed_fields)
    for dep in dependencies:
        dep_fields = set(dep.get("fields", []))
        if not dep_fields:
            query = dep.get("query", "") or dep.get("query_text", "")
            if query:
                dep_fields = extract_fields(query)
        if changed_set.intersection(dep_fields):
            affected.append(dep)
    return affected

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
                'dependency_name': dep.name or dep.consumer_name,
                'dependency_id': dep.id,
                'affected_columns': [c.column_name for c in affected_cols],
                'criticality': dep.criticality,
                'impact': impact
            })
    return impacted
