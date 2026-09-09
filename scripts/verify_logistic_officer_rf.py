import os
import json
import pandas as pd
import numpy as np
import pickle

def main():
    print("Phase L/O-1: Logistic/Officer Random Forest Verification")
    
    data_path = r"d:\VEDA\datasets\logistic_officer\raw\VEDA_Logistic_Officer_Fresh_RUL_Dataset.csv"
    output_dir = r"d:\VEDA\ml\logistic_officer\random_forest\VEDA_Logistic_Officer_RF_Phase1_Output"
    
    # 1. Load artifacts
    with open(os.path.join(output_dir, "RF_phase1_model.pkl"), "rb") as f:
        model = pickle.load(f)
        
    with open(os.path.join(output_dir, "RF_phase1_feature_columns.json"), "r") as f:
        feature_cols = json.load(f)
        
    with open(os.path.join(output_dir, "RF_phase1_risk_threshold.json"), "r") as f:
        threshold_info = json.load(f)
        threshold = threshold_info["risk_threshold"]
        
    # 2. Load dataset
    df = pd.read_csv(data_path)
    
    # 3. Load saved test predictions
    test_preds_df = pd.read_csv(os.path.join(output_dir, "RF_phase1_test_predictions.csv"))
    
    # 4. Filter test vehicles from dataset
    test_vehicles = test_preds_df["Vehicle_ID"].unique()
    df_test = df[df["Vehicle_ID"].isin(test_vehicles)].copy()
    
    # Sort to ensure matching rows
    df_test = df_test.sort_values(["Vehicle_ID", "Timestamp"]).reset_index(drop=True)
    test_preds_df = test_preds_df.sort_values(["Vehicle_ID", "Timestamp"]).reset_index(drop=True)
    
    # 5. Extract features using the exact feature contract
    X_test = df_test[feature_cols]
    
    # 6. Run inference
    probs = model.predict_proba(X_test)[:, 1]
    preds = (probs >= threshold).astype(int)
    
    # 7. Verification
    saved_probs = test_preds_df["predicted_abnormal_probability"].values
    saved_preds = test_preds_df["predicted_class"].values
    
    prob_diff = np.max(np.abs(probs - saved_probs))
    pred_diff = np.sum(preds != saved_preds)
    
    print(f"Max probability difference: {prob_diff}")
    print(f"Prediction mismatches: {pred_diff}")
    
    if prob_diff < 1e-6 and pred_diff == 0:
        print("MODEL RELOAD CONSISTENCY: PASS")
    else:
        print("MODEL RELOAD CONSISTENCY: FAIL")

if __name__ == "__main__":
    main()
