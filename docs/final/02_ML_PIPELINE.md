# 02. ML PIPELINE

## Pipeline Stages

### 1. Risk Classification (Random Forest)
All vehicles pass through a Random Forest classification gate. It evaluates a single telemetry vector to detect anomalies.
- **Tank Threshold**: `0.52`
- **Logistic/Officer Threshold**: `0.35`

### 2. Time-Series Inference
If sufficient data (30 timesteps) is provided, the payload is passed to the regression models.
- **XGBoost**: Analyzes engineered feature statistics over the window.
- **LSTM (1D-CNN + LSTM)**: Extracts deep spatial-temporal patterns from the sequence.

### 3. RUL Fusion
The outputs are deterministically fused into a single `fusion_rul_hours` metric.
- **Tank**: `1.00 × XGBoost` (XGBoost vastly outperformed LSTM due to sensor noise resistance).
- **Logistic/Officer**: `0.30 × LSTM + 0.70 × XGBoost` (Hybrid approach yields optimal MAE).

### 4. Insufficient Data Guard
If `<30 timesteps` are submitted, the pipeline mathematically halts RUL calculation, returning `null` to trigger the system's `UNKNOWN` safety state.
