# 03. AGENT ORCHESTRATION

## The `VedaOrchestrator`
Once ML inference concludes, the results are passed to a deterministic, sequential 6-agent chain.

### 1. Monitoring Agent
Evaluates the Random Forest risk score against the vehicle's specific threshold. Outputs `abnormal_detected` and `severity_score`.

### 2. Diagnostics Agent
If abnormal, evaluates the sensor payload to generate specific `active_fault_codes` (e.g., Engine, Transmission, Suspension).

### 3. Prognostics Agent
Formats and contextualizes the fused RUL. It is responsible for enforcing the `UNKNOWN` state if RUL is `null`.

### 4. Maintenance Planning Agent
Generates actionable recommendations (e.g., "Inspect Engine", "Replace Tracks") and assigns a priority (`HIGH`, `MEDIUM`, `LOW`) based on the fault codes and RUL.

### 5. Spare Parts Agent
Checks an internal inventory dictionary to see if the required components are `AVAILABLE`, `LOW_STOCK`, or `NOT_AVAILABLE`.

### 6. Fleet Readiness Agent
Aggregates the entire pipeline into a final status:
- `READY`: Normal operation.
- `ATTENTION`: Abnormalities detected but vehicle remains operational.
- `NOT_READY`: Critical failure or RUL severely depleted.
- `UNKNOWN`: Missing sequence data.
