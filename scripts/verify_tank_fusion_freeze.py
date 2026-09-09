import os
import json
import pandas as pd
import numpy as np

def verify_freeze():
    print("VERIFYING TANK FUSION FREEZE STATUS")
    output_dir = r"d:\VEDA\ml\tank\fusion\VEDA_Tank_Fusion_Phase5C_Output"
    
    config_path = os.path.join(output_dir, "fusion_config.json")
    if not os.path.exists(config_path):
        print("FAIL: config not found")
        return False
        
    with open(config_path, "r") as f:
        config = json.load(f)
        
    w_lstm = config["lstm_weight"]
    w_xgb = config["xgb_weight"]
    
    # Check weight integrity
    if not np.isclose(w_lstm + w_xgb, 1.0):
        print("FAIL: Weights do not sum to 1.0")
        return False
        
    # Check predictions
    val_preds = pd.read_csv(os.path.join(output_dir, "phase5c_fusion_validation_predictions.csv"))
    test_preds = pd.read_csv(os.path.join(output_dir, "phase5c_fusion_test_predictions.csv"))
    
    # Recalculate deterministic formula
    val_recalc = w_lstm * val_preds['LSTM_RUL'] + w_xgb * val_preds['XGB_RUL']
    test_recalc = w_lstm * test_preds['LSTM_RUL'] + w_xgb * test_preds['XGB_RUL']
    
    if not np.allclose(val_recalc, val_preds['Fusion_RUL']):
        print("FAIL: Validation predictions do not match formula")
        return False
        
    if not np.allclose(test_recalc, test_preds['Fusion_RUL']):
        print("FAIL: Test predictions do not match formula")
        return False
        
    print("TANK FUSION FREEZE STATUS: FROZEN")
    return True

if __name__ == "__main__":
    verify_freeze()
