# VEDA Agentic AI Architecture

## 1. High-Level Agent Flow
The VEDA platform bridges raw vehicle telemetry and predictive ML inferences into actionable maintenance intelligence through a structured Agentic AI pipeline.

**Flow Sequence:**
1. **Vehicle Telemetry:** Raw sensor data (measured telemetry).
2. **ML Inference Layer:** Time-series processing, scaling, and sequence extraction.
3. **Random Forest Abnormality Gate:** Routes normal vs. abnormal patterns and computes `RF_Abnormal_Probability` and `RF_Abnormal_Class`.
4. **Prognostic Models:** LSTM + 1D-CNN and XGBoost infer remaining useful life (RUL).
5. **Fusion Layer:** Combines LSTM and XGBoost prognostic outputs deterministically.
6. **Agentic Layer Execution:**
   - **Monitoring Agent** (Parallel observation)
   - **Diagnostics Agent** (Sequential after abnormality detected)
   - **Prognostics Agent** (Sequential after RUL evaluated)
   - **Maintenance Planning Agent** (Sequential after Diagnostics/Prognostics)
   - **Spare Parts Agent** (Triggered by Maintenance Planning)
   - **Fleet Readiness Agent** (Aggregates state globally)
7. **Communication / Orchestration:** Coordinates agent messages, state, and human oversight.
8. **Frontend / API / Database:** Surfaces information, logs events, and stores system history.

## 2. Tank vs. Logistic/Officer Isolation
VEDA maintains strict isolation between two model families: `tank` and `logistic_officer`.
- **Namespaces:** Data contracts, agent configurations, and telemetry events must include `model_family`.
- **Prohibited Crossover:** Tank telemetry and agent processes must NEVER load Logistic/Officer models, scalers, or weights, and vice versa. 
- **Common Schemas:** Agents use common Pydantic/JSON schemas (e.g., `PrognosticsResult`), but the model configuration artifacts executing the logic must be isolated by vehicle type.

## 3. Database / API Boundary
- **Agent Roles:** Agents read telemetry, health scores, and ML predictions from the database, and write agent events, diagnostic results, and maintenance recommendations.
- **Prohibited DB Actions:** Agents must NOT execute arbitrary DDL (migrations). They operate on defined schemas (`vehicle_health`, `faults`, `maintenance_recommendations`, etc.).
- **Backend API:** FastAPI acts as the boundary. The orchestration layer routes data to the agents; agents do not execute directly inside the API's synchronous request-response loops for long-running inference tasks.
