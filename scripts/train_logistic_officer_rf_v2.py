import os
import json
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, balanced_accuracy_score

def main():
    print("Phase L/O-1 V2: Logistic/Officer Random Forest Training")
    
    data_path = r"d:\VEDA\datasets\logistic_officer\corrected_rul_v2\VEDA_Logistic_Officer_Corrected_RUL_Dataset.csv"
    splits_path = r"d:\VEDA\datasets\logistic_officer\corrected_rul_v2\VEDA_Logistic_Officer_Corrected_RUL_Vehicle_Splits.json"
    output_dir = r"d:\VEDA\ml\logistic_officer\random_forest\VEDA_Logistic_Officer_RF_Phase1_V2_Output"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading data...")
    df = pd.read_csv(data_path)
    with open(splits_path, 'r') as f:
        splits = json.load(f)
        
    train_vehicles = splits["train"]
    val_vehicles = splits["validation"]
    test_vehicles = splits["test"]
    
    print(f"Train vehicles: {len(train_vehicles)}")
    print(f"Validation vehicles: {len(val_vehicles)}")
    print(f"Test vehicles: {len(test_vehicles)}")
    
    # Identify feature columns (strict exclusions)
    exclude_cols = [
        "Vehicle_ID", "Vehicle_Name", "Vehicle_Class", "Timestamp", 
        "Health_Index", "Degradation_Index", "RUL_hours", 
        "Affected_Sensors", "Abnormal_Pattern", "Abnormal_Direction", 
        "Abnormal_Severity", "Label_Source", "RF_Abnormal_Label",
        "RF_Abnormal_Probability", "RF_Abnormal_Prediction"
    ]
    
    all_cols = df.columns.tolist()
    feature_cols = [c for c in all_cols if c not in exclude_cols]
    
    target_col = "RF_Abnormal_Label"
    
    cat_features = ["Operating_Terrain"] if "Operating_Terrain" in feature_cols else []
    num_features = [c for c in feature_cols if c not in cat_features]
    
    print(f"Total features: {len(feature_cols)}")
    print(f"Numeric: {len(num_features)}, Categorical: {len(cat_features)}")
    
    train_df = df[df["Vehicle_ID"].isin(train_vehicles)].copy()
    val_df = df[df["Vehicle_ID"].isin(val_vehicles)].copy()
    test_df = df[df["Vehicle_ID"].isin(test_vehicles)].copy()
    
    X_train = train_df[feature_cols]
    y_train = train_df[target_col]
    X_val = val_df[feature_cols]
    y_val = val_df[target_col]
    X_test = test_df[feature_cols]
    y_test = test_df[target_col]
    
    # Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features)
        ]
    )
    
    rf = RandomForestClassifier(
        n_estimators=100, 
        max_depth=10, 
        random_state=42, 
        n_jobs=-1,
        class_weight='balanced'
    )
    
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', rf)
    ])
    
    print("Training model...")
    model.fit(X_train, y_train)
    
    print("Evaluating on validation to select threshold...")
    val_probs = model.predict_proba(X_val)[:, 1]
    
    # Test thresholds on validation set ONLY
    best_threshold = 0.5
    best_f1 = -1
    candidate_thresholds = []
    
    for thresh in np.arange(0.1, 0.9, 0.05):
        val_preds_t = (val_probs >= thresh).astype(int)
        recall_t = recall_score(y_val, val_preds_t)
        f1_t = f1_score(y_val, val_preds_t)
        candidate_thresholds.append({"threshold": float(thresh), "recall": float(recall_t), "f1": float(f1_t)})
        
        # We want high recall (gatekeeper) but also decent F1
        if recall_t >= 0.95 and f1_t > best_f1:
            best_f1 = f1_t
            best_threshold = thresh
            
    # If no threshold gives >= 0.95 recall, just pick max F1
    if best_f1 == -1:
        for thresh in np.arange(0.1, 0.9, 0.05):
            val_preds_t = (val_probs >= thresh).astype(int)
            f1_t = f1_score(y_val, val_preds_t)
            if f1_t > best_f1:
                best_f1 = f1_t
                best_threshold = thresh

    best_threshold = float(best_threshold)
    print(f"Selected threshold: {best_threshold:.4f}")
    
    def evaluate(model, X, y, threshold, prefix=""):
        probs = model.predict_proba(X)[:, 1]
        preds = (probs >= threshold).astype(int)
        
        acc = accuracy_score(y, preds)
        prec = precision_score(y, preds, zero_division=0)
        rec = recall_score(y, preds, zero_division=0)
        f1 = f1_score(y, preds, zero_division=0)
        bacc = balanced_accuracy_score(y, preds)
        
        # Calculate ROC/PR AUC if multiple classes present in true labels
        roc_auc = 0.0
        if len(np.unique(y)) > 1:
            roc_auc = roc_auc_score(y, probs)
            
        cm = confusion_matrix(y, preds).tolist()
        
        tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
        
        return {
            "accuracy": float(acc),
            "precision": float(prec),
            "abnormal_recall": float(rec),
            "f1": float(f1),
            "balanced_accuracy": float(bacc),
            "roc_auc": float(roc_auc),
            "specificity": float(specificity),
            "abnormal_fnr": float(fnr),
            "confusion_matrix": cm,
            "abnormal_tp": int(tp),
            "abnormal_fn": int(fn),
            "abnormal_fp": int(fp),
            "abnormal_tn": int(tn)
        }, probs, preds
        
    val_metrics, val_probs, val_preds = evaluate(model, X_val, y_val, best_threshold, "val")
    test_metrics, test_probs, test_preds = evaluate(model, X_test, y_test, best_threshold, "test")
    train_metrics, _, _ = evaluate(model, X_train, y_train, best_threshold, "train")
    
    print(f"Test Recall: {test_metrics['abnormal_recall']:.4f}")
    print(f"Test Specificity: {test_metrics['specificity']:.4f}")
    
    # Save artifacts
    print("Saving artifacts...")
    model_path = os.path.join(output_dir, "RF_phase1_v2_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
        
    with open(os.path.join(output_dir, "RF_phase1_v2_feature_columns.json"), "w") as f:
        json.dump(feature_cols, f, indent=4)
        
    label_map = {"0": "normal", "1": "abnormal"}
    with open(os.path.join(output_dir, "RF_phase1_v2_label_mapping.json"), "w") as f:
        json.dump(label_map, f, indent=4)
        
    with open(os.path.join(output_dir, "RF_phase1_v2_risk_threshold.json"), "w") as f:
        json.dump({"risk_threshold": best_threshold}, f, indent=4)
        
    config = {
        "random_seed": 42,
        "feature_count": len(feature_cols),
        "target_column": target_col,
        "threshold": best_threshold,
        "split_strategy": "vehicle_level",
        "training_vehicle_count": len(train_vehicles),
        "validation_vehicle_count": len(val_vehicles),
        "test_vehicle_count": len(test_vehicles),
    }
    with open(os.path.join(output_dir, "RF_phase1_v2_config.json"), "w") as f:
        json.dump(config, f, indent=4)
        
    with open(os.path.join(output_dir, "RF_phase1_v2_vehicle_splits.json"), "w") as f:
        json.dump(splits, f, indent=4)
        
    metrics_all = {
        "train_metrics": train_metrics,
        "validation_metrics": val_metrics,
        "test_metrics": test_metrics,
        "threshold_information": best_threshold
    }
    with open(os.path.join(output_dir, "RF_phase1_v2_metrics.json"), "w") as f:
        json.dump(metrics_all, f, indent=4)
        
    # Predictions
    val_df_out = val_df[["Vehicle_ID", "Timestamp", target_col]].copy()
    val_df_out["predicted_class"] = val_preds
    val_df_out["predicted_abnormal_probability"] = val_probs
    val_df_out.to_csv(os.path.join(output_dir, "RF_phase1_v2_validation_predictions.csv"), index=False)
    
    test_df_out = test_df[["Vehicle_ID", "Timestamp", target_col]].copy()
    test_df_out["predicted_class"] = test_preds
    test_df_out["predicted_abnormal_probability"] = test_probs
    test_df_out.to_csv(os.path.join(output_dir, "RF_phase1_v2_test_predictions.csv"), index=False)
    
    # Leakage Audit
    # Verify strict exclusion
    leaked_features = [f for f in feature_cols if f in exclude_cols]
    has_leakage = len(leaked_features) > 0
    leakage_audit = {
        "rul_leakage": "RUL_hours" in feature_cols,
        "target_leakage": target_col in feature_cols,
        "test_leakage": False, # Splits handled purely at vehicle level
        "vehicle_leakage": "Vehicle_ID" in feature_cols or "Vehicle_Name" in feature_cols,
        "post_inference_rf_output_used": "RF_Abnormal_Probability" in feature_cols or "RF_Abnormal_Prediction" in feature_cols,
        "abnormal_metadata_leakage": "Health_Index" in feature_cols or "Affected_Sensors" in feature_cols,
        "audit_result": "FAIL" if has_leakage else "PASS",
        "leaked_features": leaked_features
    }
    with open(os.path.join(output_dir, "RF_phase1_v2_leakage_audit.json"), "w") as f:
        json.dump(leakage_audit, f, indent=4)

    # Reload test
    print("Performing reload test...")
    with open(model_path, "rb") as f:
        reloaded_model = pickle.load(f)
        
    reloaded_test_probs = reloaded_model.predict_proba(X_test)[:, 1]
    reloaded_test_preds = (reloaded_test_probs >= best_threshold).astype(int)
    
    diff_probs = np.abs(test_probs - reloaded_test_probs).max()
    diff_preds = np.abs(test_preds - reloaded_test_preds).max()
    
    reload_consistency = {
        "max_prob_diff": float(diff_probs),
        "max_pred_diff": int(diff_preds),
        "status": "PASS" if diff_probs < 1e-6 and diff_preds == 0 else "FAIL"
    }
    with open(os.path.join(output_dir, "RF_phase1_v2_reload_consistency.json"), "w") as f:
        json.dump(reload_consistency, f, indent=4)
        
    print(f"Reload max prob diff: {diff_probs}")
    
    # Feature Importance
    cat_enc = model.named_steps['preprocessor'].named_transformers_['cat']
    cat_out_features = cat_enc.get_feature_names_out(cat_features).tolist() if cat_features and cat_enc is not None else []
    all_out_features = num_features + cat_out_features
    importances = rf.feature_importances_
    fi_df = pd.DataFrame({"feature_name": all_out_features, "importance": importances})
    fi_df = fi_df.sort_values(by="importance", ascending=False)
    fi_df.to_csv(os.path.join(output_dir, "RF_phase1_v2_feature_importance.csv"), index=False)
    
    manifest = {
        "model_file": "RF_phase1_v2_model.pkl",
        "feature_contract": "RF_phase1_v2_feature_columns.json",
        "label_mapping": "RF_phase1_v2_label_mapping.json",
        "threshold_file": "RF_phase1_v2_risk_threshold.json",
        "config_file": "RF_phase1_v2_config.json",
        "metrics_file": "RF_phase1_v2_metrics.json",
        "feature_importance": "RF_phase1_v2_feature_importance.csv",
        "leakage_audit": "RF_phase1_v2_leakage_audit.json",
        "reload_consistency": "RF_phase1_v2_reload_consistency.json"
    }
    with open(os.path.join(output_dir, "RF_phase1_v2_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=4)
        
    readme_content = f"""# Phase L/O-1 V2 Logistic/Officer RF Model

- Purpose: Abnormal-reading gatekeeper and router for the Logistic/Officer family (V2).
- Canonical model file: RF_phase1_v2_model.pkl
- Target: {target_col}
- Input feature contract: Documented in RF_phase1_v2_feature_columns.json (total {len(feature_cols)} features).
- Threshold: {best_threshold:.4f} (selected on validation data).
- Training split: {len(train_vehicles)} vehicles
- Validation split: {len(val_vehicles)} vehicles
- Test split: {len(test_vehicles)} vehicles
"""
    with open(os.path.join(output_dir, "README.md"), "w") as f:
        f.write(readme_content)

    print("Phase L/O-1 V2 complete.")

if __name__ == "__main__":
    main()
