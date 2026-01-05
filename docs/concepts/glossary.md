# Glossary

Key terms defined for OpsTwin.

---

## A

### AIW (AI Web)

A web protocol designed for easy consumption and synchronization by AI agents. Structure defined by schemas and JSON, not HTML.

### Action

A tangible operation that performs changes. E.g., Changing temperature setpoints, restarting services.

### Anomaly

A pattern deviating from the normal state. Detected via Z-Score, etc. `AnomalyDetected` event is published upon detection.

### Asset

A specific target within a Twin. E.g., Specific sensor, equipment, service instance. Identified by `asset_id`.

### Approval Workflow

The process of obtaining human approval when conditions for automatic execution are not met.

---

## C

### Confidence Score

A trust score (0.0 ~ 1.0) aggregating data quality, simulation consistency, and AI consensus.

### Cursor

A position marker in the event stream indicating "processed up to here". Format: `cursor_000123`.

---

## D

### Decision Maker

A component that routes decisions to `auto_execute`, `require_approval`, `require_analysis`, or `reject` based on confidence scores.

### Diff

A synchronization method returning only changed events/resources after a specific point (cursor).

### Digital Twin

A virtual representation (software abstraction) of real systems/equipment. Synchronized with real-time data.

---

## E

### Event

A specific occurrence in the system. E.g., `TelemetryAppended`, `AnomalyDetected`, `ActionSucceeded`.

### Event Log

A sequentially recorded log of all state changes. Diffs are generated storage on this log.

---

## H

### Hybrid Coupler

A router that selects between classical and quantum simulation engines based on the situation.

---

## K

### KPI (Key Performance Indicator)

Key metrics for performance. E.g., Yield, utilization, cost, energy efficiency.

---

## M

### Manifest

The service's self-description document. Includes provided endpoints, schemas, and permissions. `/.well-known/aiw-manifest.json`.

### Monte Carlo

A simulation technique calculating uncertainty through random sampling. Provides distribution and percentile results.

---

## P

### Policy

Rules for automation and permissions. Includes RBAC roles, thresholds, and safety constraints.

### Proposal

A suggestion to "execute this action". Includes reasoning and expected effects. Created when approval is needed.

---

## R

### RBAC (Role-Based Access Control)

Access control based on roles. Roles: viewer, agent, executor, supervisor, admin.

### Rollback

A mechanism to revert to a previous state upon action failure or policy violation.

---

## S

### Schema

A specification defining data structure (JSON Schema). E.g., `telemetry.v1`, `anomaly.v1`.

### Schema Registry

A component that manages and validates registered schemas.

### SSE (Server-Sent Events)

A technology where the server pushes real-time events to the client.

### Subscribe

An endpoint receiving real-time event streams via SSE. `/subscribe`.

---

## T

### Telemetry

Time-series data like sensors/logs/metrics. The minimum unit of Observation.

### Twin

Abbreviation for Digital Twin. All events belong to a `twin_id`.

---

## Related Documents

- [What is OpsTwin?](what-is-opstwin.md)
- [Architecture Overview](architecture.md)
- [Quick Start](../getting-started/quick-start.md)
