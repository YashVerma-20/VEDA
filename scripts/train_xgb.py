import os
import json
import pickle
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Paths
dataset_dir = r"d:\VEDA\datasets\tank\downstream"
output_dir = r"d:\VEDA\ml\tank\xgboost\VEDA_Tank_XGB_Phase3_Output"
os.makedirs(output_dir, exist_ok=True)

print("Loading data...")
X_train = pd.read_csv(os.path.join(dataset_dir, "xgb_train.csv"))
X_val = pd.read_csv(os.path.join(dataset_dir, "xgb_validation.csv"))
X_test = pd.read_csv(os.path.join(dataset_dir, "xgb_test.csv"))

y_train = np.load(os.path.join(dataset_dir, "lstm_cnn_y_train.npy")).ravel()
y_val = np.load(os.path.join(dataset_dir, "lstm_cnn_y_validation.npy")).ravel()
y_test = np.load(os.path.join(dataset_dir, "lstm_cnn_y_test.npy")).ravel()

test_meta = pd.read_csv(os.path.join(dataset_dir, "test_metadata.csv"))

# We load feature columns just to save them
with open(os.path.join(dataset_dir, "xgb_feature_columns.json"), 'r') as f:
    feature_cols = json.load(f)

# Define candidates
candidates = [
    {"max_depth": 4, "learning_rate": 0.1, "n_estimators": 100},
    {"max_depth": 6, "learning_rate": 0.1, "n_estimators": 100},
    {"max_depth": 4, "learning_rate": 0.05, "n_estimators": 150}
]

print("Starting candidate evaluation...")
best_candidate = None
best_val_mae = float('inf')
candidate_results = []

for i, params in enumerate(candidates):
    print(f"Training Candidate {i+1}: {params}")
    model = xgb.XGBRegressor(
        **params,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    val_preds = model.predict(X_val)
    val_mae = mean_absolute_error(y_val, val_preds)
    val_rmse = np.sqrt(mean_squared_error(y_val, val_preds))
    
    candidate_results.append({
        "candidate_id": i+1,
        "params": params,
        "val_mae": val_mae,
        "val_rmse": val_rmse
    })
    print(f"Candidate {i+1} Val MAE: {val_mae:.4f}")
    
    if val_mae < best_val_mae:
        best_val_mae = val_mae
        best_candidate = {
            "model": model,
            "params": params,
            "id": i+1,
            "val_mae": val_mae,
            "val_rmse": val_rmse
        }

print(f"\nBest Candidate: {best_candidate['id']} with MAE: {best_val_mae:.4f}")

# Final Evaluation on Test Set
final_model = best_candidate['model']
test_preds = final_model.predict(X_test)

test_mae = mean_absolute_error(y_test, test_preds)
test_rmse = np.sqrt(mean_squared_error(y_test, test_preds))
test_r2 = r2_score(y_test, test_preds)

print(f"Final Test MAE: {test_mae:.4f}")
print(f"Final Test RMSE: {test_rmse:.4f}")
print(f"Final Test R2: {test_r2:.4f}")

# Save metrics
metrics = {
    "validation_mae": best_candidate['val_mae'],
    "validation_rmse": best_candidate['val_rmse'],
    "test_mae": test_mae,
    "test_rmse": test_rmse,
    "test_r2": test_r2
}
with open(os.path.join(output_dir, "xgb_test_metrics.json"), "w") as f:
    json.dump(metrics, f, indent=4)

with open(os.path.join(output_dir, "candidate_results.json"), "w") as f:
    json.dump(candidate_results, f, indent=4)

# Per-vehicle test metrics
test_meta['y_true'] = y_test
test_meta['y_pred'] = test_preds
vehicle_metrics = []
for vehicle_id, group in test_meta.groupby('Vehicle_ID'):
    v_mae = mean_absolute_error(group['y_true'], group['y_pred'])
    v_rmse = np.sqrt(mean_squared_error(group['y_true'], group['y_pred']))
    vehicle_metrics.append({
        "vehicle_id": str(vehicle_id),
        "mae": v_mae,
        "rmse": v_rmse,
        "samples": len(group)
    })
pd.DataFrame(vehicle_metrics).to_csv(os.path.join(output_dir, "per_vehicle_metrics.csv"), index=False)

# Save predictions
test_meta[['Vehicle_ID', 'Start_Timestamp', 'y_true', 'y_pred']].to_csv(os.path.join(output_dir, "test_predictions.csv"), index=False)


# Feature Importance
importance = final_model.feature_importances_
feat_imp_df = pd.DataFrame({
    "feature": feature_cols,
    "importance": importance
}).sort_values(by="importance", ascending=False)
feat_imp_df.to_csv(os.path.join(output_dir, "feature_importance.csv"), index=False)

# Plot Feature Importance (Top 30)
plt.figure(figsize=(10, 8))
top_n = feat_imp_df.head(30)
plt.barh(top_n['feature'][::-1], top_n['importance'][::-1])
plt.xlabel("XGBoost Importance")
plt.title("Top 30 Feature Importances")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "feature_importance.png"))
plt.close()

# Plot Actual vs Predicted
plt.figure(figsize=(8, 6))
plt.scatter(y_test, test_preds, alpha=0.3, s=10)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
plt.xlabel("Actual RUL")
plt.ylabel("Predicted RUL")
plt.title("Actual vs Predicted RUL (Test Set)")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "actual_vs_predicted.png"))
plt.close()

# Save Config
config = {
    "model_type": "XGBRegressor",
    "input_shape": [1350],
    "best_params": best_candidate['params'],
    "feature_count": 1350
}
with open(os.path.join(output_dir, "xgb_config.json"), "w") as f:
    json.dump(config, f, indent=4)

with open(os.path.join(output_dir, "feature_ordering.json"), "w") as f:
    json.dump(feature_cols, f, indent=4)

# Save Model
final_model.save_model(os.path.join(output_dir, "veda_tank_xgboost_model.json"))

print("Training script finished successfully. Artifacts saved.")
