# VEDA Monitoring Agent

## 1. Purpose
The Monitoring Agent is the first step in the Agentic AI pipeline. Its primary role is to observe incoming vehicle telemetry streams alongside the available frozen ML inference results (specifically Random Forest abnormality classifications) to identify overall vehicle state. 

The Monitoring Agent does **NOT**:
- Calculate RUL.
- Root-cause failures.
- Fabricate missing data.
- Execute maintenance logic.

## 2. Inputs
The agent expects a strictly typed `MonitoringInput` schema via the service interface:
- `vehicle_id` (string)
- `vehicle_class` (string: strictly "TANK", "LOGISTIC", or "OFFICER")
- `timestamp` (datetime)
- `telemetry` (dict of numerical sensor readings)
- `rf_abnormal_probability` (float, optional)
- `rf_abnormal_prediction` (int, optional)

*All inputs are validated using Pydantic. Any inclusion of prohibited ground-truth fields (like `Actual_RUL` or `Health_Index`) will result in an explicit `ValidationError`.*

## 3. Outputs
The agent returns a `MonitoringResult`:
- `vehicle_id`
- `vehicle_class`
- `timestamp`
- `abnormal_detected` (bool)
- `severity` (string: "NORMAL", "WARNING", "UNKNOWN")
- `observed_findings` (list of text statements)
- `source_model_info` (dict containing trace metadata like rf_probability)
- `status` (string: "SUCCESS", "UNSUPPORTED_VEHICLE", "INSUFFICIENT_DATA", "UNAVAILABLE_RF")
- `execution_metadata` (agent version and execution time)

## 4. Decision Logic & Error States
- **Unsupported Vehicle:** If the `vehicle_class` is unrecognized, the agent returns `abnormal_detected=False`, `severity=UNKNOWN`, and `status=UNSUPPORTED_VEHICLE`.
- **Missing Telemetry:** If `telemetry` is empty, returns `severity=UNKNOWN` and `status=INSUFFICIENT_DATA`.
- **Missing ML Inference:** If `rf_abnormal_prediction` is `None`, the agent does not attempt to guess or evaluate raw thresholds manually. It flags `status=UNAVAILABLE_RF`.
- **Abnormal Identification:** If `rf_abnormal_prediction == 1`, `abnormal_detected=True` and `severity=WARNING`.

## 5. Integration Boundary
The agent is currently exposed as a callable Python class `MonitoringAgent` under `backend/app/agents/monitoring/agent.py`. It is separated from the database and orchestration layers to allow unit testing in isolation. In the future, the orchestration backend API will load the data from PostgreSQL, invoke the agent's `.process()` method, and route the resulting `MonitoringResult` to the `DiagnosticsAgent`.

## 6. Test Coverage
Unit tests (`tests/test_monitoring_agent.py`) verify:
- Happy paths (normal operation and abnormal detection).
- Boundary limits (missing data, missing RF outputs).
- Isolation mechanisms (unrecognized vehicle classes).
- Schema integrity (preventing fabricated fields and target leakage).
