# VEDA Communication / Orchestration Layer

## 1. Purpose
The Orchestration layer coordinates the six completed VEDA agents:
1. Monitoring Agent
2. Diagnostics Agent
3. Prognostics Agent
4. Maintenance Planning Agent
5. Spare Parts Agent
6. Fleet Readiness Agent

It acts as a secure, stateless router and dependency coordinator. It is **NOT** a seventh decision-making agent. It does not calculate RUL, override diagnostic findings, or create its own business rules.

## 2. Execution Flow
The orchestrator supports both `SINGLE_VEHICLE` and `FLEET` requests.
- **Single Vehicle**: The orchestrator routes the vehicle's telemetry and ML outputs sequentially through the first five agents. The Fleet Readiness Agent is then invoked with an aggregated view of just that one vehicle.
- **Multi-Vehicle/Fleet**: The orchestrator runs the vehicle-level pipeline (Agents 1-5) for *each* vehicle in the request independently, isolating their contexts. After all vehicle pipelines complete, it passes the aggregated results to the Fleet Readiness Agent.

## 3. Dependency Handling and UNKNOWN Propagation
The orchestrator respects the conditional logic defined in Phase 5A:
- If Monitoring fails or flags data as invalid, it is passed downstream where subsequent agents naturally transition to `UNKNOWN`, `NOT_APPLICABLE`, or `CONFLICT`.
- The orchestrator **never** attempts to silently "fix" missing data (e.g., substituting missing RUL with 0 or averaging it).
- Conflicts (e.g., between Diagnostics and Monitoring) are preserved and passed to Fleet Readiness, which safely flags the vehicle state as `INDETERMINATE`.

## 4. Execution Tracing
Every request generates an `execution_trace` in the `OrchestrationResult`. The trace lists each agent invoked, the status it returned, and any caught exceptions. This provides full auditability of the pipeline.

## 5. Security and Database Boundaries
- **Routing**: The orchestrator only invokes pre-registered Python class instances. It does not support arbitrary dynamic code execution or string-based path imports from the client.
- **Persistence**: Currently, the orchestrator returns the structured state to the caller. It does not introduce new database migrations or create fake inventory/readiness tables.
- **Retry Policy**: There is no approved automatic retry policy for business logic decisions. A deterministic validation failure is handled securely and returned in the trace rather than infinitely retried.

## 6. Prohibited Operations
- No RUL recalculation or modification of Fusion V2.
- No LLM-based hidden decision layers for routing.
- No fabricated completion statuses for maintenance or procurement.
