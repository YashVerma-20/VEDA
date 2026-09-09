# Agent Contracts and Responsibilities

This document outlines the six VEDA agents, their responsibilities, and their inter-agent communication schemas.

## 1. Agent Definitions

### 1. Monitoring Agent
- **Purpose:** Monitor vehicle health state and detect events.
- **Inputs:** Vehicle telemetry, RF abnormal classifications, system status.
- **Outputs:** `MonitoringResult`
- **Dependencies:** None (first agent in the pipeline).
- **Prohibitions:** Must not invent sensor readings or fabricate failures.
- **Trigger:** Can trigger the Diagnostics Agent if an abnormality is confirmed.

### 2. Diagnostics Agent
- **Purpose:** Determine probable causes of abnormal behavior.
- **Inputs:** `MonitoringResult`, sensor patterns, RF classification outputs, fault codes.
- **Outputs:** `DiagnosticsResult`
- **Dependencies:** Monitoring Agent, Random Forest model.
- **Prohibitions:** Must not diagnose beyond available evidence.
- **Trigger:** Can trigger the Maintenance Planning Agent.

### 3. Prognostics Agent
- **Purpose:** Interpret predictive-maintenance results (RUL) and degradation risk.
- **Inputs:** `LSTM_RUL`, `XGBoost_RUL`, `Fusion_RUL`, `MonitoringResult`.
- **Outputs:** `PrognosticsResult`
- **Dependencies:** Prognostic ML models (LSTM, XGBoost, Fusion).
- **Prohibitions:** Does not replace ML models. Must not fabricate RUL values.
- **Trigger:** Can trigger the Maintenance Planning Agent based on low RUL thresholds.

### 4. Maintenance Planning Agent
- **Purpose:** Translate diagnostics and prognostics into actionable maintenance recommendations.
- **Inputs:** `DiagnosticsResult`, `PrognosticsResult`.
- **Outputs:** `MaintenancePlan`
- **Dependencies:** Diagnostics Agent, Prognostics Agent.
- **Prohibitions:** Must not claim a maintenance action was completed when it was only recommended. Must not invent schedules.
- **Trigger:** Can trigger the Spare Parts Agent.

### 5. Spare Parts Agent
- **Purpose:** Support spare-parts planning and detect shortages based on recommended maintenance.
- **Inputs:** `MaintenancePlan`, inventory state (read-only query).
- **Outputs:** `SparePartsRequirement`
- **Dependencies:** Maintenance Planning Agent, Database Inventory.
- **Prohibitions:** Never invent inventory quantities or fabricate parts availability.

### 6. Fleet Readiness Agent
- **Purpose:** Provide fleet-level readiness summaries and identify high-risk vehicles.
- **Inputs:** `PrognosticsResult`, `MaintenancePlan`, fleet-wide metrics.
- **Outputs:** `FleetReadinessStatus`
- **Dependencies:** Prognostics and Maintenance Agents across multiple vehicles.
- **Prohibitions:** Must not invent readiness scores unsupported by individual vehicle statuses.

## 2. Inter-Agent Data Contracts (Schemas)

The following represent the schema fields passed between agents.

**MonitoringResult**
- `vehicle_id` (string)
- `vehicle_class` (string)
- `timestamp` (datetime)
- `rf_abnormal_probability` (float, optional)
- `rf_abnormal_prediction` (int, optional)
- `abnormal_detected` (bool)
- `severity` (string)

**DiagnosticsResult**
- `vehicle_id` (string)
- `timestamp` (datetime)
- `problem_detected` (string)
- `evidence_sensors` (list of strings)
- `probable_cause` (string)
- `confidence` (float, optional - only if derived from RF probability)
- `next_diagnostic_action` (string)

**PrognosticsResult**
- `vehicle_id` (string)
- `timestamp` (datetime)
- `fusion_rul_hours` (float, required if models available)
- `lstm_rul_hours` (float, optional)
- `xgb_rul_hours` (float, optional)
- `degradation_trend` (string)
- `risk_level` (string)

**MaintenancePlan**
- `vehicle_id` (string)
- `timestamp` (datetime)
- `recommended_action` (string)
- `priority` (string: LOW, MEDIUM, HIGH, CRITICAL)
- `reason` (string, tracing back to diagnostics/prognostics)
- `estimated_time_frame_hours` (float)

**SparePartsRequirement**
- `vehicle_id` (string)
- `recommended_action_reference` (string)
- `required_parts` (list of strings)
- `inventory_available` (bool)
- `shortage_detected` (bool)

**FleetReadinessStatus**
- `timestamp` (datetime)
- `total_vehicles` (int)
- `mission_ready_count` (int)
- `maintenance_required_count` (int)
- `high_risk_vehicles` (list of strings)

**AgentExecutionMetadata**
- `agent_name` (string)
- `execution_timestamp` (datetime)
- `status` (string: SUCCESS, FAILED, UNAVAILABLE)
- `fallback_triggered` (bool)
