# VEDA Maintenance Planning Agent

## 1. Purpose
The Maintenance Planning Agent is a recommendation layer that evaluates diagnostic and prognostic intelligence to propose maintenance actions. It acts as the fourth stage in the Agentic AI pipeline.

The Maintenance Planning Agent does **NOT**:
- Execute maintenance.
- Claim maintenance was completed.
- Make spare-part or inventory decisions.
- Make fleet-level readiness decisions.
- Calculate RUL or invent maintenance intervals (e.g., "replace after X hours").

## 2. Upstream Dependencies
The agent consumes outputs strictly from the preceding layers:
- `MonitoringResult`
- `DiagnosticsResult`
- `PrognosticsResult`

It depends heavily on the interpreted state from these agents. If an upstream agent flags data as `CONFLICT` or `INVALID`, the Maintenance Planning Agent propagates the conflict and refuses to issue a planned recommendation without resolving the contradiction.

## 3. Inputs
The agent expects a strictly typed `MaintenancePlanningInput` schema:
- `monitoring_result` (`MonitoringResult` object)
- `diagnostics_result` (`DiagnosticsResult` object)
- `prognostics_result` (`PrognosticsResult` object)

*All inputs are validated using Pydantic.*

## 4. Outputs
The agent returns a `MaintenancePlan`:
- `vehicle_id`
- `timestamp`
- `recommended_action` (string: high-level recommendation statement)
- `priority` (string: "UNKNOWN" unless a specific policy rule is loaded)
- `reason` (string: trace logic mapping back to diagnostic/prognostic input)
- `estimated_time_frame_hours` (Optional[float]: Always None unless explicit policy dictates otherwise)
- `maintenance_status` (string: "UNKNOWN" or "RECOMMENDED")
- `constraints_missing_info` (list of strings: specifies what external policies or future agents, like Spare Parts, are required to finalize the plan)
- `status` (string: "SUCCESS", "CONFLICT")
- `execution_metadata`

## 5. RUL and Approved-Rule Boundary
The agent explicitly does **not** recalculate RUL or apply arbitrary thresholds (e.g., RUL < 100 -> Critical). It only responds to `OBSERVED_DEGRADATION` trends and `TRIGGER_MAINTENANCE_PLANNING` diagnostic actions. If preventative maintenance is recommended, it explicitly adds a constraint that "approved preventative maintenance policy" is required to proceed.

## 6. Vehicle Isolation
The logic framework is completely generic and isolated. The orchestration layer guarantees that Logistic/Officer data does not intersect with Tank data.

## 7. Test Coverage
Unit tests (`tests/test_maintenance_planning_agent.py`) verify:
- Prohibition against generating "COMPLETED" maintenance statuses.
- Propagation of conflict states.
- Strict reliance on upstream evidence without inventing repair duration thresholds.
