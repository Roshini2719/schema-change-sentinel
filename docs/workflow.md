# Workflow Documentation

## 🌊 End-to-End Data Flow

1. **Data Arrival**: External partner data arrives at the staging area.
2. **Schema Inference**: Schema Sentinel infers the schema of the incoming dataset.
3. **Contract Evaluation**: The inferred schema is compared against the registered Data Contract.
4. **Dependency Check**: Any discrepancies are mapped against downstream dependencies to assess impact.
5. **Decision**: Data is either Approved (published to Data Warehouse) or Rejected (quarantined).

## 📝 Schema Registration Workflow

1. Data Engineer logs into the Schema Sentinel dashboard.
2. Navigates to **Contracts** -> **New Contract**.
3. Defines the expected schema (columns, types, nullability) for a specific partner feed.
4. Links downstream consumers (BI reports, ML models) to specific required columns.
5. Saves the contract.

## 🚀 Pipeline Run Workflow

1. Airflow (or another orchestrator) triggers a data ingestion task.
2. Before loading the data, the orchestrator calls the Schema Sentinel `POST /api/validate` endpoint.
3. Schema Sentinel responds with a JSON payload indicating `status: SAFE` or `status: UNSAFE`, along with detailed diffs.
4. The orchestrator routes the data based on the status.

## 🛑 Publication Gate Workflow

- **Status SAFE**: Pipeline proceeds to the Load phase.
- **Status UNSAFE**: Pipeline halts the Load phase. The data is moved to a quarantine bucket.
- **Alerting**: An alert is generated detailing exactly which contract failed and which downstream consumers are impacted.

## 🔑 Override Workflow

Sometimes, an urgent business need requires bypassing the gate temporarily.
1. Admin or Data Engineer views the blocked payload in the dashboard.
2. They select **Force Publish**.
3. They must enter a justification reason.
4. The action is permanently recorded in the Audit Log, and the data is released to the Data Warehouse.

## 👥 Role-Based Workflows

- **Admin**: Can manage organizations, users, and override system blocks.
- **Data Engineer**: Manages Data Contracts, schema definitions, and resolves pipeline blockages.
- **Analyst**: Views dependencies, registers downstream consumer requirements, and queries audit logs.
- **Partner**: View-only access to their specific schema contracts and historical rejections (helps them fix their data faster).

## 🎬 Demo Workflow

The built-in demo mode walks users through the lifecycle of schema changes:
1. Initialize the database with demo seed data.
2. Execute Scenario 1 (Normal Data): Observe green path.
3. Execute Scenario 2 (Breaking Change): Observe red path and quarantine.
4. Explore Audit Logs and Dependency graphs to understand the *why* behind the decision.
