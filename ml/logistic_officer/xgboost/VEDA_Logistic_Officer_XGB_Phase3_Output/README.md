# Phase L/O-3 Logistic/Officer XGBoost Model

- Purpose: Tabular nonlinear fallback and feature importance prognostic model for Logistic/Officer vehicles.
- Canonical model: VEDA_Logistic_Officer_XGB_Phase3_model.json
- Target: RUL_hours at the sequence endpoint.
- Input: Flattened (N, 840) dimensions derived from the 28 feature L/O-2 downstream sequences.
- Model Selection: Validation MAE used to pick from 3 predefined configurations.
- Test Metrics: MAE 105.4795, RMSE 131.5658, R2 -0.0136
