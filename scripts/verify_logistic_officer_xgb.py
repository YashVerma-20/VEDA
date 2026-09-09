import os
import pandas as pd
import numpy as np
from xgboost import XGBRegressor

def main():
    print("Phase L/O-3: Logistic/Officer XGBoost Reload Verification")
    
    npz_dir = r"d:\VEDA\datasets\logistic_officer\downstream"
    output_dir = r"d:\VEDA\ml\logistic_officer\xgboost\VEDA_Logistic_Officer_XGB_Phase3_Output"
    
    # 1. Load artifacts
    model_path = os.path.join(output_dir, "VEDA_Logistic_Officer_XGB_Phase3_model.json")
    model = XGBRegressor()
    model.load_model(model_path)
    
    # 2. Load dataset
    test_data = np.load(os.path.join(npz_dir, "downstream_test_lstm_1dcnn.npz"), allow_pickle=True)
    X_test = test_data["X"].reshape(test_data["X"].shape[0], -1)
    
    # 3. Load saved test predictions
    test_preds_df = pd.read_csv(os.path.join(output_dir, "phase3_xgb_test_predictions.csv"))
    
    # 4. Run inference
    preds = model.predict(X_test)
    
    # 5. Verification
    saved_preds = test_preds_df["Predicted_RUL"].values
    
    pred_diff = np.max(np.abs(preds - saved_preds))
    print(f"Max prediction difference: {pred_diff}")
    
    if pred_diff < 1e-4:
        print("MODEL RELOAD CONSISTENCY: PASS")
    else:
        print("MODEL RELOAD CONSISTENCY: FAIL")

if __name__ == "__main__":
    main()
