# OpsTwin.aiw Technical Specification v0.3 (MVP Implementation Complete)

> **Target Audience:** *AI Agents/Developers/Reviewers encountering OpsTwin for the first time*.
> **Goal:** (1) Define Core AIW Concepts → (2) Clarify what OpsTwin provides → (3) Present immediately implementable API/Schema/Flow/Security requirements.

---

## MVP Implementation Status (v0.3 Update)

### ✅ Implementation Complete

| Module | Implementation Path | Status |
|------|----------|------|
| AIW Protocol | `src/opstwin/aiw/` | ✅ Done |
| Telemetry Layer | `src/opstwin/telemetry/` | ✅ Done |
| Policy Layer | `src/opstwin/policy/` | ✅ Done |
| Simulation Engine | `src/opstwin/simulation/` | ✅ Done |
| API Server | `src/api/` | ✅ Done |
| Database | `redis_client.py`, `database.py` | ✅ Done |
| CI/CD | `.github/workflows/ci.yml` | ✅ Done |

### 📊 Test Status

- 49 Test Cases (100% PASSED)
- Unit Tests: AIW(13), Telemetry(9), Policy(12), Simulation(9)
- Integration Tests: E2E Flow(6)

---

## 0. At a Glance

### 0.1 One-Line Definition

**OpsTwin.aiw** is an **Operational Optimization Execution Platform** that builds a **Digital Twin** from *real-time telemetry*, performs **simulation-based (classical+quantum) decision making**, automates **Propose/Approve/Execute (Action)** workflows according to **Policy**, and allows external AI agents to continuously synchronize all changes via **AIW methods (Manifest + Schema + Diff/Stream)**.

### 0.2 Problems Solved

- Operational data flows in real-time, but decisions are delayed by "Reports/Meetings/Humans".
- Changes (parameter tuning/routing/deployment/resource allocation) are hard to automate due to risk (cost of failure).
- Hard to track "Why a decision was made (Reasoning)" and "What changed (Diff)".
- Knowledge/Policy sharing between multiple AIs (or sites/factories) is slow and unstable.

### 0.3 Core Ideas

- **Delta-first**: Standard is **Diff and Event Stream**, not "Full Page".
- **Schema-first**: **Machine-readable Schemas** (JSON Schema) are first-class citizens, not human-readable docs.
- **Policy-first**: Automated execution is limited by policy; Permissions/Approval/Audit/Rollback are part of the standard flow.
- **Twin-first**: Real assets are abstracted as Twin objects; all events belong to a Twin/Asset.
- **Hybrid Sim**: Quantum acceleration is an option only when cost-effective (not always quantum).

---

## 1. AIW Primer (Minimal Concepts for AI-Friendly Web)

> This section is a minimal definition for "AIs seeing AIW for the first time".
> OpsTwin operates as an **AIW Service** and follows AIW principles.

### 1.1 What is AIW?

**AIW (AI Web)** is a web designed for **AI agents to consume, synchronize, and execute immediately**, replacing "human-friendly web pages (HTML-centric)".
AIW is defined by a **Protocol Contract**, not a domain extension:

1) **Manifest (Self-Description)**: Declares resources, schemas, permissions, and endpoints provided by the service.
2) **Schema (Specification)**: Explicit data structures via JSON Schema (machine-verifiable).
3) **Diff/Stream (Delta-Centric)**: Subscribe to **changes and events** instead of repeated full queries.
4) **Action (Optional)**: Handles not just reading but "Propose/Approve/Execute", with mandatory permission/audit/rollback.

### 1.2 Minimum AIW Contract (OpsTwin Must Provide) - ✅ Implemented

| Endpoint | Implementation File | Status |
|-----------|----------|------|
| `GET /.well-known/aiw-manifest.json` | `routes/manifest.py` | ✅ |
| `GET /schemas` | `routes/manifest.py` | ✅ |
| `GET /schemas/{name}` | `routes/manifest.py` | ✅ |
| `GET /diff?since={cursor}` | `routes/diff.py` | ✅ |
| `GET /subscribe` | `routes/diff.py` | ✅ |

---

## 2. Module Details

### 2.1 AIW Protocol (`src/opstwin/aiw/`)

| File | Class/Function | Description |
|------|------------|------|
| `manifest.py` | `ManifestBuilder`, `build_manifest()` | Generate Manifest JSON |
| `diff_stream.py` | `DiffEngine`, `CursorManager` | Delta Sync, Cursor Mgmt |
| `schema_registry.py` | `SchemaRegistry` | Schema Registration/Validation |
| `sse_publisher.py` | `SSEPublisher` | SSE Event Publishing |

### 2.2 Telemetry Layer (`src/opstwin/telemetry/`)

| File | Class/Function | Description |
|------|------------|------|
| `sensor_adapter.py` | `MQTTSensorAdapter` | MQTT Sensor Connection |
| `event_normalizer.py` | `EventNormalizer` | Format conversion to telemetry.v1 |
| `anomaly_detector.py` | `AnomalyDetector` | Z-Score based Anomaly Detection |
| `timeseries_db.py` | `TimeSeriesDB` | TimescaleDB Adapter |

### 2.3 Policy Engine (`src/opstwin/policy/`)

| File | Class/Function | Description |
|------|------------|------|
| `permission_model.py` | `PermissionChecker` | RBAC 5 Roles (viewer→admin) |
| `confidence_scorer.py` | `ConfidenceScorer` | 4-Component Weighted Confidence |
| `decision_maker.py` | `DecisionMaker` | auto/approve/analyze/reject |
| `approval_workflow.py` | `ApprovalWorkflow` | Proposal Creation/Approval/Rejection |

### 2.4 Simulation Engine (`src/opstwin/simulation/`)

| File | Class/Function | Description |
|------|------------|------|
| `monte_carlo.py` | `MonteCarloEngine` | 10K Samples, 4 Distributions, Convergence Check |
| `hybrid_coupler.py` | `HybridCoupler` | Classical/Quantum Routing, Recommendation Generation |

---

## 3. API Endpoints (Implemented)

### 3.1 AIW Protocol

```
GET  /.well-known/aiw-manifest.json   # Service Discovery
GET  /schemas                          # List Schemas
GET  /schemas/{name}                   # Get Schema
GET  /diff?since={cursor}              # Delta Sync
GET  /subscribe                        # SSE Stream
```

### 3.2 Telemetry

```
POST /telemetry/ingest                 # Ingest Telemetry
GET  /telemetry/query                  # Query Telemetry
GET  /telemetry/aggregate              # Time-series Aggregation
```

### 3.3 Simulation

```
POST /sim/run                          # Run Simulation
```

### 3.4 System

```
GET  /health                           # Health Check
```

---

## 4. Data Schemas (Implemented)

### 4.1 telemetry.v1

```json
{
  "event_id": "tel_01H...",
  "twin_id": "factory_line_3",
  "asset_id": "etch_tool_7",
  "ts": "2026-01-04T12:34:56Z",
  "metrics": {"temp_c": 62.1, "pressure_pa": 101325},
  "tags": {"process_step": "etch"},
  "quality": {"data_quality_score": 0.97}
}
```

### 4.2 anomaly.v1

```json
{
  "anomaly_id": "ano_01H...",
  "twin_id": "factory_line_3",
  "asset_id": "etch_tool_7",
  "ts": "2026-01-04T12:35:10Z",
  "score": 0.93,
  "kind": "drift",
  "severity": "high",
  "features": {"temp_c_z": 3.2},
  "recommended_next": "sim_run"
}
```

---

## 5. Policy Engine (Implemented)

### 5.1 Role Hierarchy (RBAC)

```
admin → supervisor/executor → agent → viewer
```

### 5.2 Decision Thresholds

```python
THRESHOLDS = {
    "auto_execute": 0.90,     # Confidence ≥0.90 → Auto Execute
    "require_approval": 0.70, # 0.70 ≤ Confidence < 0.90 → Approval Required
}
```

### 5.3 Confidence Calculation (4 Components)

```python
WEIGHTS = {
    "historical_success_rate": 0.25,
    "data_quality_score": 0.25,
    "simulation_consistency": 0.30,
    "ai_consensus_score": 0.20,
}
```

---

## 6. Simulation Engine (Implemented)

### 6.1 MonteCarloEngine

- Samples: Default 10,000
- Distributions: normal, uniform, triangular, lognormal
- Percentiles: p5, p25, p50, p75, p95, p99
- Convergence: Relative Standard Error < 1%

### 6.2 HybridCoupler

- Engine Selection: classical (default), quantum (if Qiskit available)
- Recommendation: Based on performance + uncertainty

---

## 7. Execution

### 7.1 Local Development

```bash
pip install -e ".[dev]"
uvicorn src.api.main:app --reload --port 8000
pytest tests/ -v
```

### 7.2 Docker

```bash
cd docker
docker-compose up -d
```

---

## 8. Project Structure

```
AI_Web/
├── .github/workflows/ci.yml    # CI/CD
├── pyproject.toml              # Project Config
├── README.md
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── schemas/
│   └── telemetry_v1.json
├── src/
│   ├── api/                    # FastAPI Routes
│   ├── opstwin/                # Core Modules
│   │   ├── aiw/
│   │   ├── telemetry/
│   │   ├── policy/
│   │   └── simulation/
│   └── ppr/                    # PPR Definitions (63 items)
└── tests/                      # 49 Tests
```

---

## 9. Next Steps (v0.4 Roadmap)

### 9.1 High Priority

- [ ] Proposal/Action Endpoint Implementation
- [ ] Rollback Mechanism
- [ ] Federation Layer Basics

### 9.2 Medium Priority

- [ ] Kafka Integration
- [ ] Real Quantum Backend Integration (IBM Quantum)
- [ ] K8s Deployment Manifests

### 9.3 Low Priority

- [ ] Human Dashboard UI
- [ ] Multi-tenancy Support

---

**Doc Version**: OpsTwin.aiw Technical Spec v0.3 (MVP Complete)
**Date**: 2026-01-04 (Asia/Seoul)
