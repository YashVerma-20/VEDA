# Phase 5C: Tank Fusion Implementation & Validation

## 1. Background
During Phase 6A/6B, an ML to Agentic AI integration audit was performed to verify if the frozen ML models could be integrated into the new orchestrator. It was discovered that the `ml/tank/fusion` directory was entirely empty. The deterministic Fusion layer for the Tank namespace had never been implemented in any prior phase.

## 2. Why Tank Fusion was required
The VEDA Predictive Maintenance architecture (specifically the Model-Agent Contract defined in Phase 5A) strictly requires a unified `Fusion_RUL` passed into the Agentic layer (specifically the Prognostics Agent). Without a frozen Tank Fusion formula, the backend ML Inference service would fail to compile the final `VehicleOrchestrationRequest`.

## 3. Existing frozen upstream models
The newly created fusion layer relies entirely on the pre-existing, frozen models:
- **Tank LSTM + 1DCNN**: `ml/tank/lstm_1dcnn/Model 2 Current Best/VEDA_Phase5B_LSTM_1DCNN_final.keras`
- **Tank XGBoost**: `ml/tank/xgboost/VEDA_Tank_XGB_Phase3_Output/veda_tank_xgboost_model.json`
*No upstream models were retrained, modified, or overwritten during this phase.*

## 4. Validation data
To properly select fusion weights without leaking the test set, validation datasets were loaded:
- `lstm_cnn_X_validation.npy` (30 timesteps, 45 features per window)
- `xgb_validation.csv` (1350 flattened features per window)
- `validation_metadata.csv` (contains actual RUL targets, sequence indices, and vehicle IDs).

## 5. Alignment methodology
Before combining predictions, the output arrays from the LSTM and XGBoost models were evaluated against `validation_metadata.csv`. Both arrays aligned exactly to the expected `3768` samples spread across `8` unique validation vehicles, proving perfect window alignment.

## 6. Leakage prevention
The dataset was loaded strictly for **inference**. The training algorithm did not optimize or fit any trainable parameters. The RUL was only used for error calculation (MAE/RMSE/R2) after the predictions were already generated. The test dataset was untouched until the validation weights were permanently frozen.

## 7. Candidate Fusion strategies
A simple deterministic weighted average strategy was employed:
`Fusion_RUL = w * LSTM_RUL + (1 - w) * XGB_RUL`

## 8. Weight sweep
The weight `w` was swept from `0.00` to `1.00` using a `0.05` increment size. This avoids spurious overfitting to validation noise and aligns with project methodology.

## 9. Weight selection methodology
The singular primary selection metric was **Validation Mean Absolute Error (MAE)**.

## 10. Complete validation results
(Extracted from `validation_candidates.json`)
```
w_LSTM   | w_XGB    | MAE      | RMSE     | R2      
--------------------------------------------------
0.00     | 1.00     | 226.0278 | 327.3143 | 0.6863  
0.05     | 0.95     | 231.6955 | 320.5085 | 0.6992  
0.10     | 0.90     | 242.6661 | 321.1493 | 0.6980  
0.15     | 0.85     | 258.1204 | 329.1932 | 0.6827  
...
0.50     | 0.50     | 431.3963 | 529.1035 | 0.1803 
...
0.95     | 0.05     | 732.6863 | 920.6547 | -1.4818 
1.00     | 0.00     | 770.2656 | 966.8394 | -1.7370 
```

## 11. Selected weight
- `w_LSTM` = **0.00**
- `w_XGB` = **1.00**
The XGBoost model out-performed the LSTM model so drastically on the validation set that any inclusion of the LSTM degraded performance. Thus, the purely XGBoost prediction was mathematically selected.

## 12. Validation performance
- **LSTM Validation MAE**: 770.2657
- **XGBoost Validation MAE**: 226.0278
- **Fusion Validation MAE**: 226.0278

## 13. Test performance
- **LSTM Test MAE**: 827.4634
- **XGBoost Test MAE**: 204.7630
- **Fusion Test MAE**: 204.7630 (RMSE: 282.0088, R2: 0.8087)

## 14. LSTM vs XGB vs Fusion
Fusion mathematically aligns entirely with XGBoost due to the 0.00/1.00 weight split. The Tank LSTM severely underperforms in this specific pipeline.

## 15. Complementarity analysis
Because `w_LSTM` = 0.00, the models are not complementary in a way that improves MAE. The XGBoost model contains significantly better predictive capability in the Tank namespace. Fusion does not improve over the strongest standalone model, which is XGBoost. 

## 16. Deterministic formula
```
Fusion_RUL = 0.00 * LSTM_RUL + 1.00 * XGB_RUL
```

## 17. Artifact locations
All Phase 5C artifacts are saved in:
`ml/tank/fusion/VEDA_Tank_Fusion_Phase5C_Output/`
- `fusion_config.json`
- `validation_candidates.json`
- `validation_metrics.json`
- `test_metrics.json`
- `phase5c_fusion_validation_predictions.csv`
- `phase5c_fusion_test_predictions.csv`

## 18. Freeze verification
The `scripts/verify_tank_fusion_freeze.py` script was written to independently verify that the exact deterministic formula mathematically computes the saved fusion outputs. It successfully outputted `TANK FUSION FREEZE STATUS: FROZEN`.

## 19. Limitations
Due to the poor predictive performance of the original Tank LSTM, the deterministic fusion layer acts simply as a passthrough for the XGBoost model. 

*No Tank Fusion implementation existed before Phase 5C. This phase created a new deterministic Fusion layer using predictions from the already-frozen Tank LSTM + 1D-CNN and Tank XGBoost models. No upstream Tank ML model was retrained or modified.*
