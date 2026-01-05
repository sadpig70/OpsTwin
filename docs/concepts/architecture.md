# OpsTwin Architecture

## System Overview

OpsTwin consists of 6 core layers, each with clear roles and responsibilities.

```mermaid
graph TD
    User[External AI Agents] -->|Manifest / Schema| AIW[AIW Protocol Layer]
    User -->|Diff / Subscribe| AIW
    
    subgraph "Core Engine (FastAPI)"
        AIW -->|Routes| API[API Server]
        
        API --> Telemetry[Telemetry Layer]
        API --> Policy[Policy Engine]
        API --> Sim[Simulation Engine]
        
        Telemetry -->|Anomaly Event| Policy
        Telemetry -->|Anomaly Event| Sim
        Sim -->|Sim Completed| Policy
        Policy -->|Decision| Action[Action Executor]
    end
    
    subgraph "Data Layer"
        Telemetry -->|Store/Query| TSDB[(TimescaleDB)]
        AIW -->|Cursor/Cache| Redis[(Redis)]
        Telemetry -->|Stream| MQTT[MQTT Broker]
    end

    classDef core fill:#d4e1f5,stroke:#333,stroke-width:2px;
    classDef data fill:#e1f5d4,stroke:#333,stroke-width:2px;
    classDef user fill:#f5d4d4,stroke:#333,stroke-width:2px;
    
    class AIW,API,Telemetry,Policy,Sim,Action core;
    class TSDB,Redis,MQTT data;
    class User user;
```

---

## Module Details

### 1. AIW Protocol Layer (`src/opstwin/aiw/`)

Handles communication with AI Agents.

| Component | File | Role |
| :--- | :--- | :--- |
| Manifest | `manifest.py` | Service Self-Description (Discovery) |
| DiffStream | `diff_stream.py` | Delta Sync, Cursor Management |
| SchemaRegistry | `schema_registry.py` | Schema Registration/Validation |
| SSEPublisher | `sse_publisher.py` | Real-time Event Publishing |

### 2. Telemetry Layer (`src/opstwin/telemetry/`)

Handles sensor data collection and processing.

| Component | File | Role |
| :--- | :--- | :--- |
| SensorAdapter | `sensor_adapter.py` | Sensor Connection (MQTT) |
| EventNormalizer | `event_normalizer.py` | Data Normalization |
| AnomalyDetector | `anomaly_detector.py` | Anomaly Detection (Z-Score) |
| TimeSeriesDB | `timeseries_db.py` | Time-series Storage |

### 3. Policy Engine (`src/opstwin/policy/`)

Manages automation rules and permissions.

| Component | File | Role |
| :--- | :--- | :--- |
| PermissionChecker | `permission_model.py` | RBAC Permission Check |
| ConfidenceScorer | `confidence_scorer.py` | Confidence Calculation |
| DecisionMaker | `decision_maker.py` | Decision Routing |
| ApprovalWorkflow | `approval_workflow.py` | Approval Workflow |

### 4. Simulation Engine (`src/opstwin/simulation/`)

Performs What-if analysis.

| Component | File | Role |
| :--- | :--- | :--- |
| MonteCarloEngine | `monte_carlo.py` | Monte Carlo Simulation |
| HybridCoupler | `hybrid_coupler.py` | Classical/Quantum Engine Selection |

---

## Data Flow (Event-Driven)

```mermaid
sequenceDiagram
    participant Sensor
    participant Telemetry
    participant Sim as Simulation
    participant Policy
    participant AIW as Diff/Stream

    Sensor->>Telemetry: 1. Raw Data (MQTT/HTTP)
    Telemetry->>Telemetry: Normalize & Store
    Telemetry->>Telemetry: Detect Anomaly
    
    alt Anomaly Detected
        Telemetry->>AIW: 2. Publish AnomalyDetected
        Telemetry->>Sim: 3. Trigger Simulation
        Sim->>Sim: Run Monte Carlo / Quantum
        Sim->>Policy: 4. SimulationCompleted (KPIs)
        
        Policy->>Policy: Calculate Confidence
        Policy->>Policy: Evaluate Rules
        
        alt Confidence >= Threshold
            Policy->>AIW: 5. Auto Execute Action
        else Low Confidence
            Policy->>AIW: 5. Request Approval
        end
    else Normal State
        Telemetry->>AIW: Publish TelemetryAppended
    end
```

---

## Deployment Architecture

### Docker Compose Configuration

```yaml
services:
  opstwin:     # FastAPI Server (8000)
  redis:       # Cursor/Caching (6379)
  timescaledb: # Time-series DB (5432)
  kafka:       # Event Streaming (Optional)
```

### Scalability

- **Horizontal Scaling**: Multiple instances of FastAPI Server
- **Partitioning**: Sharding based on twin_id
- **Caching**: Caching simulation results with Redis

---

## Tech Stack

| Area | Technology |
| :--- | :--- |
| API | FastAPI 0.109+ |
| Database | TimescaleDB 2.x, Redis 7.x |
| Message Queue | Kafka 3.x (Optional) |
| Simulation | NumPy, Qiskit (Optional) |
| Testing | pytest 8.x |
| Container | Docker 24.x |

---

## Next Steps

- [Quick Start](../getting-started/quick-start.md)
- [API Reference](http://localhost:8000/docs)
- [Glossary](glossary.md)
