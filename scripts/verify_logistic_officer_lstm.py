import os
import pandas as pd
import numpy as np
import tensorflow as tf

def main():
    print("Phase L/O-2: Logistic/Officer LSTM Reload Verification")
    
    npz_dir = r"d:\VEDA\datasets\logistic_officer\downstream"
    output_dir = r"d:\VEDA\ml\logistic_officer\lstm_1dcnn\VEDA_Logistic_Officer_LSTM_1DCNN_Phase2_Output"
    
    # 1. Load artifacts
    model_path = os.path.join(output_dir, "VEDA_Logistic_Officer_LSTM_1DCNN_final.keras")
    model = tf.keras.models.load_model(model_path)
    
    # 2. Load dataset
    test_data = np.load(os.path.join(npz_dir, "downstream_test_lstm_1dcnn.npz"), allow_pickle=True)
    X_test = test_data["X"]
    
    # 3. Load saved test predictions
    test_preds_df = pd.read_csv(os.path.join(output_dir, "phase2_lstm_1dcnn_test_predictions.csv"))
    
    # 4. Run inference
    preds = model.predict(X_test).flatten()
    
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
