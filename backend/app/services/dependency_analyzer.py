import re
from typing import Dict, Any, List, Set

def extract_fields_from_query(query: str) -> Set[str]:
    """Extract field names from a SQL query string."""
    fields = set()
    # match common sql identifiers, ignore keywords (very basic regex)
    words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', query)
    keywords = {"select", "from", "where", "and", "or", "group", "by", "order", "having", "sum", "avg", "count", "min", "max", "as", "on", "join", "left", "right", "inner"}
    for word in words:
        if word.lower() not in keywords:
            fields.add(word)
    return fields

def analyze_dependencies(
    changed_fields: List[str],
    dependencies: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Analyze impact of changed fields on downstream dependencies."""
    affected = []
    has_critical = False
    
    changed_set = set(changed_fields)
    
    for dep in dependencies:
        dep_fields = set(dep.get("fields", []))
        if not dep_fields:
            query = dep.get("query_text", "")
            if query:
                dep_fields = extract_fields_from_query(query)
                
        intersection = changed_set.intersection(dep_fields)
        if intersection:
            affected.append({
                "name": dep.get("name", "unknown"),
                "affected_fields": list(intersection),
                "criticality": dep.get("criticality", "medium")
            })
            if dep.get("criticality", "").lower() == "critical":
                has_critical = True
                
    return {
        "affected_dependencies": affected,
        "total_affected": len(affected),
        "has_critical": has_critical
    }
