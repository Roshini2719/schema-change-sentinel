# Problem Analysis

## 📌 Background and Context

In modern data ecosystems, organizations ingest data from dozens to thousands of external partners. These partners supply critical data streams (e.g., financial transactions, user events, supply chain updates).

Because external partners control their systems independently, their data schemas inevitably evolve. Columns are added, deleted, or renamed; data types are altered; constraints are modified.

## 💥 Industry Impact

When a partner changes a schema without prior notification, the change cascades through the ingestion pipeline. 
If the pipeline is not explicitly checking for schema drift, it may successfully process the malformed data and load it into the Data Warehouse.

This leads to:
1. **Silent Failures**: Downstream consumers (BI tools, ML models) compute results on missing or incorrect data, leading to flawed business decisions.
2. **Financial Loss**: In fintech, missing a critical field (like a transaction fee or a currency code) can result in direct financial discrepancies.
3. **Operational Overhead**: Data engineers spend countless hours tracing the source of corrupted data, rolling back pipelines, and manually backfilling data.

## 📉 Current Approaches and Limitations

1. **Schema-less Ingestion (JSON/NoSQL)**
   - *Approach*: Dump everything into a NoSQL store or a JSON column.
   - *Limitation*: Pushes the burden of validation to the downstream consumer, causing runtime errors in BI tools and ML models.

2. **Strict ETL (Extract, Transform, Load)**
   - *Approach*: Pipeline crashes immediately upon unexpected schema.
   - *Limitation*: Brittle. Non-breaking changes (like adding a new optional column) will halt the entire pipeline unnecessarily, leading to data staleness.

3. **Basic Schema Validation**
   - *Approach*: Check if schema exactly matches expectations.
   - *Limitation*: Lacks context. Not all changes are breaking.

## 🔍 Why Schema Validation Alone is Insufficient

Basic schema validation treats all changes equally. It does not understand the *impact* of a change. For example:
- Dropping an unused column is safe.
- Dropping a column used in a critical financial report is a disaster.
Without knowing downstream dependencies, validation systems are either too strict (blocking safe changes) or too lenient (allowing unsafe changes).

## 🕸️ Why Dependency Analysis Matters

Dependency analysis bridges the gap between the producer and the consumer. By mapping exactly which downstream systems consume which columns, Schema Sentinel can intelligently classify changes:
- If Column X is deleted, and no consumer requires Column X, the change is **ALLOWED**.
- If Column Y is deleted, and Consumer Z requires Column Y, the change is **BLOCKED**, and Consumer Z is alerted.

## 🛡️ Why Fail-Closed is Important in Fintech

In fintech applications, the cost of processing incorrect data is significantly higher than the cost of delaying data processing.
- **Fail-Open**: If the validation system is down, let data pass through. (High Risk)
- **Fail-Closed**: If the validation system cannot definitively prove the data is safe, block it. (High Safety)
Schema Sentinel adopts a strict fail-closed philosophy to protect the integrity of financial systems.
