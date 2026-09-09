# Phase L/O-2 Logistic/Officer LSTM + 1D-CNN Model

- Purpose: Prognostic model for RUL prediction in the Logistic/Officer family.
- Canonical model: VEDA_Logistic_Officer_LSTM_1DCNN_final.keras
- Input contract: Sequence length 30, 28 features (includes RF generated probabilities/predictions).
- Target: RUL_hours at the end of the sequence.
- Preprocessing: StandardScaler and OneHotEncoder fitted on training split only.
- Splitting:
  - Train: 23304 sequences
  - Validation: 7768 sequences
  - Test: 7768 sequences
- Metrics (Test): MAE 126.7843, RMSE 161.7262, R2 -0.5316
