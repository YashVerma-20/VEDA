# Phase 6A: ML → Agent Integration Audit

## 1. Audit Objective
The purpose of this audit is to verify the integration boundary between the frozen ML pipelines (Tank and Logistic/Officer) and the Agentic AI layer. The goal is to determine if real ML inference outputs can be passed to the agents via approved contracts and to identify any integration blockers.

## 2. System Architecture Reviewed
- **Tank Pipeline:** `ml/tank/` (RF, LSTM, XGBoost, Fusion)
- **Logistic/Officer Pipeline:** `ml/logistic_officer/` (RF V2, LSTM V2, XGBoost V2, Fusion V2)
- **Agentic AI Layer:** `backend/app/agents/` (Monitoring, Diagnostics, Prognostics, Maintenance Planning, Spare Parts, Fleet Readiness, Orchestration)

## 3. Tank Integration Findings
- **RF:** BLOCKED. The `RF_phase4_model.pkl` artifact can be loaded using `joblib` (though there is a scikit-learn version mismatch warning), but there is no implementation of a model inference wrapper in the service layer to execute preprocessing and prediction.
- **LSTM:** BLOCKED. Artifacts exist, but no inference service connects telemetry to the model.
- **XGBoost:** BLOCKED. No inference service exists.
- **Fusion:** BLOCKED. No inference service exists to execute the fusion formula in runtime before hitting the agents.

## 4. Logistic/Officer Integration Findings
- **RF:** BLOCKED. The `RF_phase1_v2_model.pkl` artifact can be loaded, but no wrapper exists.
- **LSTM:** BLOCKED.
- **XGBoost:** BLOCKED.
- **Fusion:** BLOCKED. The formula (0.30 × LSTM_RUL + 0.70 × XGB_RUL) is defined in documentation, but there is no runtime component executing this logic on live telemetry.

## 5. Model → Agent Contracts
- **Status:** PASS (Contractual Level), BLOCKED (Runtime Level).
- The Pydantic schemas in `VehicleOrchestrationRequest` properly expect `rf_abnormal_probability`, `rf_abnormal_prediction`, and `fusion_rul_hours`.
- However, the mapping from raw model tensors/dataframes to these schemas is missing.

## 6. Prognostics Integration
- **Status:** PASS. The Prognostics Agent correctly consumes `fusion_rul_hours` from its input contract without recalculating it.

## 7. Maintenance Planning Integration
- **Status:** PASS. Consumes inputs without recalculating RUL or fabricating repair actions.

## 8. Spare Parts Status
- **Status:** NOT_IMPLEMENTED (as intended). Returns `UNKNOWN` or `NOT_AVAILABLE`.

## 9. Fleet Readiness Integration
- **Status:** PASS. The "demo_v1" policy is correctly integrated and applies dummy configurable thresholds without modifying upstream model outputs.

## 10. Orchestration Integration
- **Status:** PARTIAL. The Orchestrator correctly routes data between the six agents deterministically, but it does not invoke ML inference. It expects pre-computed ML outputs.

## 11. Real Artifact Inference Results
- **Status:** BLOCKED. We successfully loaded the Tank RF Phase 4 and Logistic Officer RF V2 models via a script (`joblib.load()`).
- However, real inference could not be executed because the system lacks a preprocessing and inference service wrapper to transform raw telemetry into model inputs.

## 12. Error Handling
- **Status:** PASS. The Agent layer correctly propagates `UNKNOWN` and `INSUFFICIENT_EVIDENCE` states when ML data is missing.

## 13. Tank/L-O Isolation
- **Status:** PASS. The schemas enforce `vehicle_class`, ensuring downstream logic respects namespaces.

## 14. Frozen ML Verification
- **Status:** PASS. No ML artifacts or Fusion formulas were modified during this audit.

## 15. Missing Components
- **ML Inference Service Wrapper:** The backend lacks a service that receives raw telemetry, identifies the namespace, loads the appropriate preprocessors and models, runs the RF classification, routes to the regression models, calculates Fusion RUL, and constructs the `VehicleOrchestrationRequest`.

## 16. Blockers
- Real ML -> Agent data flow is entirely blocked by the absence of an ML inference service.

## 17. Recommendations for Phase 6B
- Implement `backend/app/services/ml_inference_service.py` to act as the bridge between raw telemetry and the `VehicleOrchestrationRequest`.
- Use the frozen preprocessing objects (scalers) and artifacts to build deterministic inference wrappers for Tank and Logistic/Officer.
- Define a unified `InferencePipeline` class for each namespace that executes the approved ML topology (RF -> LSTM/XGB -> Fusion).
