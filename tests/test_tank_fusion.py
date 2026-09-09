import os
import json
import numpy as np
import pandas as pd
import pytest

OUTPUT_DIR = r"d:\VEDA\ml\tank\fusion\VEDA_Tank_Fusion_Phase5C_Output"

def test_fusion_config_exists():
    assert os.path.exists(os.path.join(OUTPUT_DIR, "fusion_config.json"))

def test_fusion_weights_sum_to_one():
    with open(os.path.join(OUTPUT_DIR, "fusion_config.json"), "r") as f:
        config = json.load(f)
    assert np.isclose(config["lstm_weight"] + config["xgb_weight"], 1.0)

def test_no_nan_in_predictions():
    val_preds = pd.read_csv(os.path.join(OUTPUT_DIR, "phase5c_fusion_validation_predictions.csv"))
    test_preds = pd.read_csv(os.path.join(OUTPUT_DIR, "phase5c_fusion_test_predictions.csv"))
    
    assert not val_preds['Fusion_RUL'].isna().any()
    assert not test_preds['Fusion_RUL'].isna().any()
    
def test_no_infinity_in_predictions():
    val_preds = pd.read_csv(os.path.join(OUTPUT_DIR, "phase5c_fusion_validation_predictions.csv"))
    test_preds = pd.read_csv(os.path.join(OUTPUT_DIR, "phase5c_fusion_test_predictions.csv"))
    
    assert not np.isinf(val_preds['Fusion_RUL']).any()
    assert not np.isinf(test_preds['Fusion_RUL']).any()

def test_deterministic_formula():
    with open(os.path.join(OUTPUT_DIR, "fusion_config.json"), "r") as f:
        config = json.load(f)
        
    w_lstm = config["lstm_weight"]
    w_xgb = config["xgb_weight"]
    
    val_preds = pd.read_csv(os.path.join(OUTPUT_DIR, "phase5c_fusion_validation_predictions.csv"))
    test_preds = pd.read_csv(os.path.join(OUTPUT_DIR, "phase5c_fusion_test_predictions.csv"))
    
    val_recalc = w_lstm * val_preds['LSTM_RUL'] + w_xgb * val_preds['XGB_RUL']
    test_recalc = w_lstm * test_preds['LSTM_RUL'] + w_xgb * test_preds['XGB_RUL']
    
    assert np.allclose(val_recalc, val_preds['Fusion_RUL'])
    assert np.allclose(test_recalc, test_preds['Fusion_RUL'])

def test_tank_namespace():
    with open(os.path.join(OUTPUT_DIR, "fusion_config.json"), "r") as f:
        config = json.load(f)
    assert config["vehicle_class"] == "TANK"

def test_upstream_artifact_integrity():
    with open(os.path.join(OUTPUT_DIR, "fusion_config.json"), "r") as f:
        config = json.load(f)
    lstm_path = os.path.join(r"d:\VEDA", config["upstream_lstm_artifact"].replace("/", "\\"))
    xgb_path = os.path.join(r"d:\VEDA", config["upstream_xgboost_artifact"].replace("/", "\\"))
    assert os.path.exists(lstm_path)
    assert os.path.exists(xgb_path)
