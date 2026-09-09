# Model to Agent Output Contract

This contract defines exactly what the Agentic AI layer receives from the ML inference layer. 
The agent layer consumes **FROZEN** ML artifacts and outputs. It does NOT train or retrain models.

## 1. Input Fields Provided to the Agent Layer

### A. Raw / Current Vehicle Telemetry
- `Timestamp`: Temporal context of the reading.
- `Vehicle_ID`: Unique identifier.
- `Sensor Readings`: Continuous numerical readings (e.g., Engine RPM, Coolant Temp).

### B. Metadata
- `Vehicle_Class` / `Model_Family`: (e.g., TANK, LOGISTIC, OFFICER).
- `Operating_Terrain`: Derived context (if applicable).

### C. Random Forest Abnormality Output
- `RF_Abnormal_Probability`: The probability (0.0 to 1.0) of abnormal behavior.
- `RF_Abnormal_Prediction`: Binary classification (0 or 1) based on the frozen threshold.
- `RF_Abnormal_Class` / `Routing_Label`: If available from the RF multi-class routing logic.

### D. LSTM Prognostic Output
- `LSTM_RUL_Prediction`: Remaining useful life predicted by the frozen LSTM + 1D-CNN model (in hours).

### E. XGBoost Prognostic Output
- `XGBoost_RUL_Prediction`: Remaining useful life predicted by the frozen XGBoost model (in hours).

### F. Fusion Output
- `Fusion_RUL_Prediction`: Deterministic weighted blend of LSTM and XGBoost predictions (e.g., `0.3 * LSTM + 0.7 * XGB`).

### G. Model Confidence / Quality
- **Constraint:** Agents receive confidence metrics *only* where an existing artifact explicitly provides them (e.g., `prediction_std` from ML evaluation metrics or RF probability). Agents MUST NOT invent or fabricate numerical confidence values.

## 2. Prohibited Inputs
Agents MUST NOT be given the following training-only or ground-truth fields:
- `Actual_RUL` / `RUL_hours` (except for test-time audit/evaluation).
- `Health_Index` (Ground truth label).
- `Degradation_Index` (Ground truth label).
- Future sensor information or future states.
- Known fault labels (e.g., `Abnormal_Pattern`, `Affected_Sensors`) unless legitimately derived by the RF model during inference.
