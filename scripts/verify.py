import os
import json
import pickle
import numpy as np
import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier

rf_dir = r"d:\VEDA\ml\tank\random_forest\VEDA_Tank_RF_Phase4_Output"
lstm_dir = r"d:\VEDA\ml\tank\lstm_1dcnn\Model 2 Current Best"

print("--- RF VERIFICATION ---")
rf_config_path = os.path.join(rf_dir, "RF_phase4_config.json")
with open(rf_config_path, 'r') as f:
    rf_config = json.load(f)

print(f"RF Config feature_count: {rf_config.get('feature_count')}")
print(f"RF Config threshold: {rf_config.get('threshold')}")

with open(os.path.join(rf_dir, "RF_phase4_feature_columns.pkl"), 'rb') as f:
    rf_features = pickle.load(f)
print(f"RF actual feature list length: {len(rf_features)}")
print(f"RF features exact order matched length: {len(rf_features)}") # Not printing all to save space, will check exact list in memory

with open(os.path.join(rf_dir, "RF_phase4_risk_threshold.pkl"), 'rb') as f:
    rf_threshold = pickle.load(f)
print(f"RF actual risk threshold: {rf_threshold}")

# Try to load models
rf_model_1_path = os.path.join(rf_dir, "RF_phase4_model.pkl")
rf_model_2_path = os.path.join(rf_dir, "model_phase4.pkl")
with open(rf_model_1_path, 'rb') as f:
    rf_model_1 = pickle.load(f)
with open(rf_model_2_path, 'rb') as f:
    rf_model_2 = pickle.load(f)

print(f"RF_phase4_model.pkl type: {type(rf_model_1)}")
print(f"model_phase4.pkl type: {type(rf_model_2)}")

# Test reload consistency for RF
test_input = np.random.rand(1, len(rf_features))
pred1 = rf_model_1.predict_proba(test_input)
pred2 = rf_model_2.predict_proba(test_input)
print(f"RF prediction 1: {pred1}")
print(f"RF prediction 2 (other file): {pred2}")

# Reload test
with open(rf_model_1_path, 'rb') as f:
    rf_model_1_reload = pickle.load(f)
pred1_reload = rf_model_1_reload.predict_proba(test_input)
print(f"RF prediction 1 after reload: {pred1_reload}")
print(f"RF duplicate files match: {np.allclose(pred1, pred2)}")
print(f"RF reload match: {np.allclose(pred1, pred1_reload)}")

print("\n--- LSTM VERIFICATION ---")
lstm_model_final_path = os.path.join(lstm_dir, "VEDA_Phase5B_LSTM_1DCNN_final.keras")
lstm_model_b1_path = os.path.join(lstm_dir, "best_B1.keras")

lstm_final = tf.keras.models.load_model(lstm_model_final_path, compile=False)
lstm_b1 = tf.keras.models.load_model(lstm_model_b1_path, compile=False)

print(f"LSTM Final Model Params: {lstm_final.count_params()}")
print(f"LSTM B1 Model Params: {lstm_b1.count_params()}")

test_input_lstm = np.random.rand(1, 30, 45).astype(np.float32)
pred_final = lstm_final.predict(test_input_lstm, verbose=0)
pred_b1 = lstm_b1.predict(test_input_lstm, verbose=0)

print(f"LSTM Final Prediction: {pred_final}")
print(f"LSTM B1 Prediction: {pred_b1}")
print(f"LSTM duplicate files match: {np.allclose(pred_final, pred_b1)}")

lstm_final_reloaded = tf.keras.models.load_model(lstm_model_final_path, compile=False)
pred_final_reloaded = lstm_final_reloaded.predict(test_input_lstm, verbose=0)
print(f"LSTM reload match: {np.allclose(pred_final, pred_final_reloaded)}")

# scaler
with open(os.path.join(lstm_dir, "feature_scaler_train_only.pkl"), 'rb') as f:
    lstm_scaler = pickle.load(f)
print(f"LSTM scaler type: {type(lstm_scaler)}")

# LSTM Architecture check
print("LSTM Final Architecture:")
for layer in lstm_final.layers:
    print(f" - {layer.name} ({layer.__class__.__name__}): {layer.output_shape}")
