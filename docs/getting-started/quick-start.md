# Quick Start

Get OpsTwin up and running and make your first API call in 5 minutes.

---

## 1. Installation

```bash
# Clone Repository
git clone <repository-url>
cd AI_Web

# Install Dependencies
pip install -e ".[dev]"
```

---

## 2. Run Server

```bash
uvicorn src.api.main:app --reload --port 8000
```

Output on success:

```
🚀 Starting OpsTwin API v0.2
✅ Redis connected
INFO: Uvicorn running on http://127.0.0.1:8000
```

---

## 3. Service Discovery

First step of AIW Protocol: Retrieve Manifest.

```bash
curl http://localhost:8000/.well-known/aiw-manifest.json
```

Response:

```json
{
  "aiw_version": "1.0",
  "service": {"name": "OpsTwin", "version": "0.2"},
  "endpoints": {
    "schemas": "/schemas",
    "diff": "/diff",
    "subscribe": "/subscribe"
  },
  "schemas": ["telemetry.v1", "anomaly.v1", ...]
}
```

---

## 4. Ingest Telemetry

Collect sensor data.

```bash
curl -X POST http://localhost:8000/telemetry/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "twin_id": "factory_line_1",
    "asset_id": "sensor_001",
    "metrics": {"temperature": 42.5, "pressure": 101.3}
  }'
```

Response:

```json
{
  "event_id": "tel_a1b2c3d4e5f6",
  "status": "accepted",
  "message": "Telemetry data ingested successfully"
}
```

---

## 5. Run Simulation

Execute Monte Carlo simulation.

```bash
curl -X POST http://localhost:8000/sim/run \
  -H "Content-Type: application/json" \
  -d '{
    "twin_id": "factory_line_1",
    "scenario": "optimization",
    "parameters": {"base_yield": 0.85}
  }'
```

Response:

```json
{
  "sim_id": "sim_x1y2z3",
  "twin_id": "factory_line_1",
  "kpi_distribution": {
    "yield": {"p50": 0.85, "p90": 0.92, "p95": 0.95}
  },
  "recommended": {
    "action": "proceed",
    "confidence": 0.87
  }
}
```

---

## 6. Subscribe to Real-time Events (SSE)

Receive changes in real-time.

```bash
curl -N http://localhost:8000/subscribe
```

Event Stream:

```
data: {"type": "TelemetryAppended", "twin_id": "factory_line_1", ...}

data: {"type": "SimulationCompleted", "sim_id": "sim_x1y2z3", ...}
```

---

## 7. Swagger UI

Check API documentation in browser.

```
http://localhost:8000/docs
```

---

## Run with Docker

```bash
cd docker
docker-compose up -d
```

Services:

- OpsTwin API: <http://localhost:8000>
- Redis: localhost:6379
- TimescaleDB: localhost:5432

---

## Next Steps

- [Architecture Overview](../concepts/architecture.md)
- [API Reference](http://localhost:8000/docs)

---

## Troubleshooting

### Redis Connection Failed

```bash
# Check Redis Service
redis-cli ping
# Output: PONG
```

### Port Conflict

```bash
# Run on different port
uvicorn src.api.main:app --port 8001
```
