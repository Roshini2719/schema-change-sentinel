# 🛡️ Schema Sentinel

**Detecting Breaking Schema Changes Before Unsafe Data Publication**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-Passing-22c55e?style=for-the-badge)

---

## 📋 Table of Contents
1. [Problem Statement](#-problem-statement)
2. [Why This Problem Matters](#-why-this-problem-matters)
3. [Solution](#-solution)
4. [Architecture](#-architecture)
5. [Technology Stack](#-technology-stack)
6. [Features](#-features)
7. [System Workflow](#-system-workflow)
8. [Schema Comparison Logic](#-schema-comparison-logic)
9. [Baseline vs Sentinel](#-baseline-vs-sentinel)
10. [Installation](#-installation)
11. [Demo Instructions](#-demo-instructions)
12. [Demo Credentials](#-demo-credentials)
13. [API Documentation](#-api-documentation)
14. [Security](#-security)
15. [Limitations](#-limitations)
16. [Future Improvements](#-future-improvements)
17. [Authors](#-authors)
18. [License](#-license)

## 🔍 Problem Statement

A fintech company ingests transaction data from multiple external partners. Partners can change their source schemas without warning — renaming columns, removing required fields, changing data types, or altering nullable constraints.

The existing data pipeline may continue running successfully even when the incoming schema has changed, creating a dangerous situation:

```
Partner → Data Pipeline → Incomplete/Incorrect Table → Downstream Consumers
```

This leads to:
- Incorrect revenue calculations
- Failed fraud detection queries  
- Broken settlement reports
- Silent data quality degradation

## ❗ Why This Problem Matters

In fintech, incorrect data can lead to:
- Financial losses from wrong calculations
- Regulatory compliance failures
- Fraud going undetected
- Customer trust erosion
- Operational disruptions

## 💡 Solution

Schema Sentinel is a schema-change detection system that:
1. **Detects** breaking upstream schema changes
2. **Analyzes** downstream dependency impact
3. **Blocks** unsafe data publication
4. **Audits** all decisions for compliance

```
Partner → Schema Sentinel → ✅ Safe → Publish
                           → 🚫 Unsafe → BLOCK + Alert + Audit
```

## 🏗️ Architecture

```
+----------------+      +-------------------+      +------------------+
|                |      |                   |      |                  |
|  External      +----->+  API Gateway /    +----->+  Schema Sentinel |
|  Partners      |      |  Ingestion Layer  |      |  Engine          |
|                |      |                   |      |                  |
+----------------+      +-------------------+      +--------+---------+
                                                            |
                                                            v
+----------------+      +-------------------+      +--------+---------+
|                |      |                   |      |                  |
|  Downstream    |<-----+  Data Warehouse / |<-----+  Publication     |
|  Consumers     |      |  Data Lake        |      |  Gate            |
|                |      |                   |      |                  |
+----------------+      +-------------------+      +------------------+
```

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.10+, FastAPI |
| Frontend | React 18, Vite, Tailwind CSS |
| Database | SQLite |
| Data Processing | Pandas, PyArrow |
| Charts | Recharts |
| Authentication | JWT (python-jose) |
| Testing | pytest, httpx |

## ✨ Features

- 🔍 **Schema Change Detection Engine** - Detects removed columns, type changes, nullable changes, PK removal
- 🚫 **Publication Gate** - Blocks unsafe data publication automatically
- 📊 **Dependency Tracking** - Maps schema changes to affected downstream consumers
- 📝 **Data Contracts** - Define and enforce what partners promise to send
- 🏢 **Multi-Tenant Support** - Multiple organisations with data isolation
- 👥 **Role-Based Access** - Admin, Data Engineer, Analyst, Partner roles
- 📋 **Audit Logging** - Complete trail of all actions and decisions
- ⚡ **Fail-Closed Safety** - If validation cannot complete, publication is blocked
- 🎯 **Demo Mode** - 7 interactive scenarios demonstrating real validation
- 📈 **Experiment Framework** - Compare baseline vs sentinel with measurable metrics

## 🔄 System Workflow

1. **Partner Integration**: Partners push data containing their schema to the ingestion layer.
2. **Schema Inference/Detection**: Sentinel infers the incoming schema and compares it against the registered Data Contract.
3. **Impact Analysis**: Any schema changes are checked against downstream dependencies to determine the blast radius.
4. **Gate Decision**: If breaking changes are found, data publication is blocked, an alert is raised, and the event is logged. Otherwise, data is published safely.

## 🔬 Schema Comparison Logic

### Breaking Changes (BLOCK)
- Required column removed → CRITICAL
- Data type changed incompatibly → CRITICAL
- Required field becomes nullable → HIGH
- Primary key removed → CRITICAL
- Required format changed → HIGH

### Non-Breaking Changes (ALLOW)
- Optional column added → INFO
- New metadata column → LOW

### Warning Changes
- Optional column removed → MEDIUM
- Enum values expanded → MEDIUM
- Precision changed → MEDIUM

## 📊 Baseline vs Sentinel

| Scenario | Baseline | Sentinel | Expected |
|----------|----------|----------|----------|
| Normal data | ✅ Published | ✅ Published | Published |
| Required column removed | ⚠️ Published | 🚫 Blocked | Blocked |
| Type changed | ⚠️ Published | 🚫 Blocked | Blocked |
| Extra column added | ✅ Published | ✅ Published | Published |
| Nullable field added | ✅ Published | ✅ Published | Published |
| PK removed | ⚠️ Published | 🚫 Blocked | Blocked |

**Key Result**: Baseline unsafe publication rate: 70% → Sentinel: 0%

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Running Experiments
```bash
python scripts/run_experiments.py
```

## 🎬 Demo Instructions

1. Log in to the application as an Admin.
2. Navigate to the **Scenarios** tab.
3. Run **Scenario 1 (Normal Data)**: Observe successful validation and publication.
4. Run **Scenario 2 (Removed Required Column)**: Observe how Sentinel blocks publication due to a missing `transaction_id`.
5. Run **Scenario 3 (Type Change)**: Observe the system blocking an integer-to-string type change for `amount`.
6. Go to the **Audit Logs** to view the trace of blocked and allowed data publications.
7. Switch to the **Dependencies** view to see which downstream consumers are impacted by the blocked changes.

## 🔑 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@finbank.com | admin123 |
| Data Engineer | engineer@finbank.com | engineer123 |
| Analyst | analyst@finbank.com | analyst123 |
| Partner | partner@partnera.com | partner123 |

## 📡 API Documentation

FastAPI auto-generates OpenAPI docs at: http://localhost:8000/docs

Key Endpoints:
- `POST /api/auth/token`: Authenticate and receive JWT.
- `GET /api/schemas`: List registered schemas.
- `POST /api/validate`: Submit schema for validation against a contract.
- `GET /api/audit`: Retrieve audit logs.

## 🔒 Security

- Password hashing with bcrypt
- JWT authentication
- Role-based authorization
- Tenant data isolation
- Input validation
- Audit logging
- No hardcoded secrets in production

**Note**: Demo credentials are for development only. Change all secrets before any production use.

## ⚠️ Limitations

- SQLite is single-writer (not suitable for high-concurrency production)
- Schema inference from CSV headers is basic
- No real-time streaming support
- Authentication is basic JWT without refresh tokens
- No email/notification integration
- Single-node deployment

## 🔮 Future Improvements

- PostgreSQL support for production
- Real-time schema monitoring with webhooks
- ML-based anomaly detection
- Integration with data catalogs (Apache Atlas, DataHub)
- Automated schema migration suggestions
- Slack/email alert integration
- API key authentication for partners
- Schema evolution policies

## 👥 Authors

- **[Your Name]** - IE28 Semester 5 Project

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file.
