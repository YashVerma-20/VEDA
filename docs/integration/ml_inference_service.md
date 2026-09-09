# ML Inference Service

## Overview
The `MLInferenceService` (located at `backend/app/services/ml_inference_service.py`) serves as the runtime bridge between raw vehicle telemetry and the Agent Orchestration layer. 

## Supported Vehicle Pipelines
The service explicitly isolates operations into two pipelines:
1. **Tank**
2. **Logistic/Officer**

Requests are routed safely via `vehicle_class`. Cross-contamination of models or preprocessing pipelines is strictly prohibited.

## Model Artifact Locations
- **Tank RF**: `ml/tank/random_forest/VEDA_Tank_RF_Phase4_Output/RF_phase4_model.pkl`
- **Tank LSTM**: `ml/tank/lstm_1dcnn/Model 2 Current Best/VEDA_Phase5B_LSTM_1DCNN_final.keras`
- **Tank XGB**: `ml/tank/xgboost/VEDA_Tank_XGB_Phase3_Output/veda_tank_xgboost_model.json`
- **Tank LSTM Preprocessor**: `ml/tank/lstm_1dcnn/Model 2 Current Best/feature_scaler_train_only.pkl` (StandardScaler)

- **L/O RF**: `ml/logistic_officer/random_forest/VEDA_Logistic_Officer_RF_Phase1_V2_Output/RF_phase1_v2_model.pkl` (Pipeline)
- **L/O LSTM**: `ml/logistic_officer/lstm_1dcnn/VEDA_Logistic_Officer_LSTM_1DCNN_Phase2_V2_Output/VEDA_Logistic_Officer_LSTM_1DCNN_V2_final.keras`
- **L/O XGB**: `ml/logistic_officer/xgboost/VEDA_Logistic_Officer_XGB_Phase3_V2_Output/VEDA_Logistic_Officer_XGB_Phase3_V2_model.json`
- **L/O Preprocessor**: `ml/logistic_officer/lstm_1dcnn/VEDA_Logistic_Officer_LSTM_1DCNN_Phase2_V2_Output/feature_scaler_train_only.pkl` (ColumnTransformer)

## Feature Contracts and Preprocessing
The service performs explicit preprocessing to match the feature dimensions expected by the artifacts. 
- Tank input telemetry receives feature engineering for variables like `Coolant_Ambient_Delta`, `Odometer_per_Hour`, `_past_mean10` (rolling mean), and `_delta1` (differences). 
- Logistic/Officer uses raw feature dictionaries for the RF model and then transforms sequences explicitly with the ColumnTransformer for sequential processing.

## Sequence Handling
The service accepts a `telemetry_df` pandas DataFrame encompassing the latest telemetry series.
- To produce prognostic Remaining Useful Life (RUL), exactly 30 timesteps are required. 
- If fewer than 30 timesteps exist, the service degrades gracefully, generating the Random Forest abnormal metrics based on the last row but outputting `None` for LSTM, XGBoost, and Fusion RUL hours.

## Random Forest Behavior
The Gatekeeper Random Forest calculates abnormality.
- **Tank Threshold**: 0.52 (dynamically loaded from artifact config)
- **L/O Threshold**: 0.35 (dynamically loaded from artifact config)

## Fusion Formulas
The deterministic frozen formulas are executed explicitly on sequential outputs.
- **Tank Fusion**: `0.00 * LSTM_RUL + 1.00 * XGB_RUL`
- **Logistic/Officer Fusion**: `0.30 * LSTM_RUL + 0.70 * XGB_RUL`

## Agent Integration
The service cleanly constructs and returns a `VehicleOrchestrationRequest`, stripping non-numeric values from the telemetry dictionary to ensure Pydantic structural validation compliance without breaking upstream functionality.

## Error Handling
- **Missing telemetry features**: Raises a `ValueError` identifying missing columns.
- **Model loading problems**: Handled gracefully. (e.g. Keras `quantization_config` deserialization bug is intercepted via python monkey patch on class deserialization, ensuring `.keras` files remain safely unmodified and frozen).
- **Insufficient sequence data**: Gracefully returns `VehicleOrchestrationRequest` without prognostic RULs.
