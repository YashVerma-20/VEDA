import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import tensorflow as tf

def main():
    print("PHASE 5C: TANK FUSION IMPLEMENTATION & VALIDATION")
    
    # 1. Paths
    dataset_dir = r"d:\VEDA\datasets\tank\downstream"
    lstm_model_path = r"d:\VEDA\ml\tank\lstm_1dcnn\Model 2 Current Best\VEDA_Phase5B_LSTM_1DCNN_final.keras"
    xgb_model_path = r"d:\VEDA\ml\tank\xgboost\VEDA_Tank_XGB_Phase3_Output\veda_tank_xgboost_model.json"
    output_dir = r"d:\VEDA\ml\tank\fusion\VEDA_Tank_Fusion_Phase5C_Output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 2. Load Datasets
    print("Loading datasets...")
    X_val_lstm = np.load(os.path.join(dataset_dir, "lstm_cnn_X_validation.npy"))
    y_val_lstm = np.load(os.path.join(dataset_dir, "lstm_cnn_y_validation.npy")).ravel()
    X_val_xgb = pd.read_csv(os.path.join(dataset_dir, "xgb_validation.csv"))
    val_meta = pd.read_csv(os.path.join(dataset_dir, "validation_metadata.csv"))
    
    X_test_lstm = np.load(os.path.join(dataset_dir, "lstm_cnn_X_test.npy"))
    y_test_lstm = np.load(os.path.join(dataset_dir, "lstm_cnn_y_test.npy")).ravel()
    X_test_xgb = pd.read_csv(os.path.join(dataset_dir, "xgb_test.csv"))
    test_meta = pd.read_csv(os.path.join(dataset_dir, "test_metadata.csv"))
    
    # Verify contracts
    assert X_val_lstm.shape[1:] == (30, 45), f"Unexpected LSTM validation shape: {X_val_lstm.shape}"
    assert X_val_xgb.shape[1] == 1350, f"Unexpected XGB validation shape: {X_val_xgb.shape}"
    
    # 3. Load Frozen Models
    print("Loading frozen models...")
    original_dense_from_config = tf.keras.layers.Dense.from_config
    def custom_dense_from_config(cls, config):
        if 'quantization_config' in config:
            del config['quantization_config']
        return original_dense_from_config(config)
    tf.keras.layers.Dense.from_config = classmethod(custom_dense_from_config)

    original_conv1d_from_config = tf.keras.layers.Conv1D.from_config
    def custom_conv1d_from_config(cls, config):
        if 'quantization_config' in config:
            del config['quantization_config']
        return original_conv1d_from_config(config)
    tf.keras.layers.Conv1D.from_config = classmethod(custom_conv1d_from_config)

    original_lstm_from_config = tf.keras.layers.LSTM.from_config
    def custom_lstm_from_config(cls, config):
        if 'quantization_config' in config:
            del config['quantization_config']
        return original_lstm_from_config(config)
    tf.keras.layers.LSTM.from_config = classmethod(custom_lstm_from_config)

    lstm_model = tf.keras.models.load_model(lstm_model_path)
    xgb_model = xgb.XGBRegressor()
    xgb_model.load_model(xgb_model_path)
    
    # 4. Generate Predictions (INFERENCE ONLY)
    print("Generating validation predictions...")
    preds_val_lstm = lstm_model.predict(X_val_lstm, batch_size=64).ravel()
    preds_val_xgb = xgb_model.predict(X_val_xgb)
    
    print("Generating test predictions...")
    preds_test_lstm = lstm_model.predict(X_test_lstm, batch_size=64).ravel()
    preds_test_xgb = xgb_model.predict(X_test_xgb)
    
    # 5. Alignment Verification
    print("Verifying alignment...")
    assert len(preds_val_lstm) == len(preds_val_xgb) == len(val_meta) == len(y_val_lstm) == 3768, "Validation length mismatch"
    assert len(val_meta['Vehicle_ID'].unique()) == 8, "Validation vehicle count mismatch"
    
    val_meta['Actual_RUL'] = y_val_lstm
    val_meta['LSTM_RUL'] = preds_val_lstm
    val_meta['XGB_RUL'] = preds_val_xgb
    
    test_meta['Actual_RUL'] = y_test_lstm
    test_meta['LSTM_RUL'] = preds_test_lstm
    test_meta['XGB_RUL'] = preds_test_xgb
    
    # 6. Candidate Strategy Evaluation
    print("Evaluating candidate strategies on VALIDATION DATA ONLY...")
    candidates = []
    best_mae = float('inf')
    best_w = None
    
    weights = np.arange(0.0, 1.05, 0.05)
    
    for w in weights:
        w_lstm = np.round(w, 2)
        w_xgb = np.round(1.0 - w_lstm, 2)
        
        fusion_preds = w_lstm * preds_val_lstm + w_xgb * preds_val_xgb
        
        mae = mean_absolute_error(y_val_lstm, fusion_preds)
        rmse = np.sqrt(mean_squared_error(y_val_lstm, fusion_preds))
        r2 = r2_score(y_val_lstm, fusion_preds)
        
        candidates.append({
            "w_lstm": w_lstm,
            "w_xgb": w_xgb,
            "val_mae": mae,
            "val_rmse": rmse,
            "val_r2": r2
        })
        
        if mae < best_mae:
            best_mae = mae
            best_w = (w_lstm, w_xgb)
        elif mae == best_mae:
            # tie-break lower rmse
            current_best = next(c for c in candidates if c["w_lstm"] == best_w[0])
            if rmse < current_best["val_rmse"]:
                best_mae = mae
                best_w = (w_lstm, w_xgb)
    
    # Document Candidates
    with open(os.path.join(output_dir, "validation_candidates.json"), "w") as f:
        json.dump(candidates, f, indent=4)
        
    print("\nValidation Results Table:")
    print(f"{'w_LSTM':<8} | {'w_XGB':<8} | {'MAE':<8} | {'RMSE':<8} | {'R2':<8}")
    print("-" * 50)
    for c in candidates:
        print(f"{c['w_lstm']:<8.2f} | {c['w_xgb']:<8.2f} | {c['val_mae']:<8.4f} | {c['val_rmse']:<8.4f} | {c['val_r2']:<8.4f}")
    
    # 7. Freeze the validation-selected weight
    w_lstm, w_xgb = best_w
    print(f"\nSELECTED WEIGHTS (Validation-only): w_LSTM={w_lstm:.2f}, w_XGB={w_xgb:.2f}")
    
    val_meta['Fusion_RUL'] = w_lstm * val_meta['LSTM_RUL'] + w_xgb * val_meta['XGB_RUL']
    
    best_cand_metrics = next(c for c in candidates if c["w_lstm"] == w_lstm)
    
    lstm_val_mae = mean_absolute_error(y_val_lstm, preds_val_lstm)
    xgb_val_mae = mean_absolute_error(y_val_lstm, preds_val_xgb)
    print(f"\nStandalone Validation MAE -> LSTM: {lstm_val_mae:.4f} | XGBoost: {xgb_val_mae:.4f}")
    
    # 8. Test Evaluation
    print("\nEvaluating on untouched Test Set...")
    test_meta['Fusion_RUL'] = w_lstm * test_meta['LSTM_RUL'] + w_xgb * test_meta['XGB_RUL']
    
    test_mae = mean_absolute_error(y_test_lstm, test_meta['Fusion_RUL'])
    test_rmse = np.sqrt(mean_squared_error(y_test_lstm, test_meta['Fusion_RUL']))
    test_r2 = r2_score(y_test_lstm, test_meta['Fusion_RUL'])
    
    lstm_test_mae = mean_absolute_error(y_test_lstm, preds_test_lstm)
    xgb_test_mae = mean_absolute_error(y_test_lstm, preds_test_xgb)
    print(f"Standalone Test MAE -> LSTM: {lstm_test_mae:.4f} | XGBoost: {xgb_test_mae:.4f}")
    print(f"Fusion Test MAE: {test_mae:.4f}, RMSE: {test_rmse:.4f}, R2: {test_r2:.4f}")
    
    # 9. Create Artifacts
    config = {
        "vehicle_class": "TANK",
        "fusion_version": "tank_fusion_phase5c",
        "method": "weighted_average",
        "lstm_weight": w_lstm,
        "xgb_weight": w_xgb,
        "selection_metric": "validation_MAE",
        "selection_dataset": "validation",
        "formula": f"Fusion_RUL = {w_lstm:.2f} * LSTM_RUL + {w_xgb:.2f} * XGB_RUL",
        "upstream_lstm_artifact": "ml/tank/lstm_1dcnn/Model 2 Current Best/VEDA_Phase5B_LSTM_1DCNN_final.keras",
        "upstream_xgboost_artifact": "ml/tank/xgboost/VEDA_Tank_XGB_Phase3_Output/veda_tank_xgboost_model.json"
    }
    
    with open(os.path.join(output_dir, "fusion_config.json"), "w") as f:
        json.dump(config, f, indent=4)
        
    val_metrics = {
        "fusion_mae": best_cand_metrics['val_mae'],
        "fusion_rmse": best_cand_metrics['val_rmse'],
        "fusion_r2": best_cand_metrics['val_r2'],
        "lstm_mae": lstm_val_mae,
        "xgb_mae": xgb_val_mae
    }
    with open(os.path.join(output_dir, "validation_metrics.json"), "w") as f:
        json.dump(val_metrics, f, indent=4)
        
    test_metrics_dict = {
        "fusion_mae": test_mae,
        "fusion_rmse": test_rmse,
        "fusion_r2": test_r2,
        "lstm_mae": lstm_test_mae,
        "xgb_mae": xgb_test_mae
    }
    with open(os.path.join(output_dir, "test_metrics.json"), "w") as f:
        json.dump(test_metrics_dict, f, indent=4)
        
    val_meta.to_csv(os.path.join(output_dir, "phase5c_fusion_validation_predictions.csv"), index=False)
    test_meta.to_csv(os.path.join(output_dir, "phase5c_fusion_test_predictions.csv"), index=False)
    
    print("\nPhase 5C Tank Fusion Artifacts Generated Successfully.")

if __name__ == "__main__":
    main()
