# Architecture Documentation

## 🏗️ System Overview

Schema Sentinel is a defensive layer that sits between external data ingestion and downstream data consumers. It ensures that schema changes from external partners do not inadvertently break internal analytical workflows, machine learning models, or reporting systems.

```ascii
+--------------------+        +---------------------+        +--------------------+
|                    |        |                     |        |                    |
|   External APIs /  +------->+   Ingestion Layer   +------->+  Schema Sentinel   |
|   Partner Data     |        |   (Kafka/S3/HTTP)   |        |  (Validation Gate) |
|                    |        |                     |        |                    |
+--------------------+        +---------------------+        +---------+----------+
                                                                       |
                                                                       | (Safe / Unsafe)
                                                                       v
+--------------------+        +---------------------+        +---------+----------+
|                    |        |                     |        |                    |
| Downstream Systems |<-------+   Data Warehouse /  |<-------+  Publication Gate  |
| (BI, ML, Reports)  |        |   Data Lake         |        |                    |
|                    |        |                     |        |                    |
+--------------------+        +---------------------+        +--------------------+
```

## 📦 Component Descriptions

### 1. Ingestion Layer
The entry point for all partner data. Data can be pushed via HTTP APIs or polled from S3/Kafka. This layer is responsible for raw data extraction.

### 2. Schema Sentinel (Validation Gate)
The core component of this project. It performs the following tasks:
- **Schema Inference**: Infers the schema (columns, types, constraints) from the incoming payload.
- **Contract Matching**: Looks up the expected Data Contract for the given partner.
- **Diff Generation**: Computes the difference between the incoming schema and the contract.
- **Dependency Tracking**: Evaluates if the detected changes break any downstream dependencies (e.g., a required column missing).

### 3. Publication Gate
A binary decision-maker:
- **Safe**: Forwards the data to the Data Warehouse.
- **Unsafe**: Blocks the data, triggers alerts, and logs the incident in the Audit Trail.

### 4. Downstream Systems
Consumers of the data (BI dashboards, ML models, etc.) which register their requirements (Data Contracts) with Schema Sentinel.

## 🔄 Data Flow

1. **Partner X** uploads `transactions.csv` to the Ingestion API.
2. Ingestion API routes the payload to **Schema Sentinel**.
3. Schema Sentinel identifies Partner X and fetches the `transaction_contract_v1`.
4. Schema Sentinel compares the payload schema against `transaction_contract_v1`.
5. If the schema matches or has only non-breaking changes (like new optional columns), the Publication Gate **allows** it.
6. If a required column (`amount`) is missing, the Publication Gate **blocks** it.
7. An **Audit Log** entry is created detailing the outcome.

## 🗄️ Database Schema Documentation

The system uses a relational model to track organizations, users, schemas, contracts, and audit events.

- `organizations`: Multi-tenant boundary.
- `users`: Role-based entities within an organization.
- `schemas`: Registered schema definitions.
- `contracts`: Rules governing schema evolution and downstream requirements.
- `audit_logs`: Immutable ledger of all validation events.

## 🔌 API Design Principles

- **RESTful**: standard HTTP verbs and status codes.
- **Stateless**: JWT-based authentication.
- **Idempotent**: Safe retries for validation endpoints.
- **Fail-closed**: If the API encounters an internal error during validation, it defaults to returning `UNSAFE`.

## 🔒 Security Architecture

- **Authentication**: JWT tokens signed with a secret key.
- **Authorization**: Role-Based Access Control (RBAC). Admin, Data Engineer, Analyst, Partner.
- **Tenant Isolation**: All queries are scoped to `organization_id`.
- **Secret Management**: Passwords are hashed using `bcrypt`. No hardcoded secrets in the codebase.

## 🏢 Multi-Tenant Architecture

Schema Sentinel is designed to support multiple organizations (tenants).
- Each tenant has its own isolated workspace.
- The `organization_id` acts as a partition key across all major tables.
- Cross-tenant access is strictly forbidden at the database and application layer.
