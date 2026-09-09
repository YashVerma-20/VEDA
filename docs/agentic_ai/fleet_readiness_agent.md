# VEDA Fleet Readiness Agent

## 1. Purpose
The Fleet Readiness Agent evaluates the operational readiness state of individual vehicles and the fleet as a whole. It acts as the sixth stage in the Agentic AI pipeline.

The Fleet Readiness Agent does **NOT**:
- Invent readiness rules or thresholds (e.g., minimum RUL for deployment).
- Assume that a healthy diagnostic state guarantees mission readiness.
- Override upstream diagnostic or prognostic results.
- Calculate RUL or modify Fusion weights.

## 2. Upstream Dependencies
The agent expects a composite `FleetReadinessInput` containing data for multiple vehicles. Each vehicle's data may include:
- `MonitoringResult`
- `DiagnosticsResult`
- `PrognosticsResult`
- `MaintenancePlan`
- `SparePartsRequirement`

## 3. Readiness and Aggregation Policy Boundaries
**CRITICAL NOTE:** The current implementation uses a **DUMMY/DEMONSTRATION** policy configurable via `config.py`. 
It is **NOT** an official military or organizational readiness standard.

The agent operates under strict constraints:
- `readiness_status`: Evaluates deterministically (READY, ATTENTION, NOT_READY, UNKNOWN).
- Configurable thresholds for RUL and fleet percentages.
- It refuses to invent data. Missing crucial upstream inputs immediately trigger an `UNKNOWN` evaluation.

## 4. Inputs
The agent expects a strictly typed `FleetReadinessInput` schema containing a dictionary of `VehicleReadinessInput` objects.
*Inputs are strictly validated.*

## 5. Outputs
The agent returns a `FleetReadinessStatus`:
- `fleet_id`
- `timestamp`
- `readiness_status` (string: "INDETERMINATE")
- `readiness_reason` (string: explicit explanation of missing policy)
- `affected_vehicles` (list of strings: vehicles flagged by upstream monitoring)
- `vehicle_summaries` (dict: vehicle-level statuses, currently all "INDETERMINATE")
- `source_information` (dict indicating false for readiness/aggregation policy availability)
- `execution_metadata`

## 6. Vehicle Isolation & ML Boundary
The agent maintains strict isolation by iterating over vehicle namespaces without intermingling rules. It treats all upstream RUL and ML evidence as read-only.

## 7. Test Coverage
Unit tests (`tests/test_fleet_readiness_agent.py`) verify:
- Prohibition against generating "READY" or "NOT_READY" without an approved policy.
- Safe handling of empty fleet inputs.
- Safe extraction of affected vehicle IDs from upstream data without asserting mission impact.
