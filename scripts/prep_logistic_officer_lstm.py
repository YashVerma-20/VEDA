import os
import json
import pandas as pd
import numpy as np
import pickle
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

def create_sequences(df, features_matrix, seq_length=30):
    sequences = []
    targets = []
    meta_vehicle_id = []
    meta_start_time = []
    meta_end_time = []
    meta_seq_id = []
    
    seq_counter = 0
    grouped = df.groupby("Vehicle_ID")
    for vehicle_id, group in grouped:
        # Assumes group is already sorted by Timestamp
        group_indices = group.index.values
        
        # We need at least seq_length rows for a sequence
        if len(group) < seq_length:
            continue
            
        for i in range(len(group) - seq_length + 1):
            seq_idx = group_indices[i : i + seq_length]
            seq_x = features_matrix[seq_idx]
            
            target_idx = group_indices[i + seq_length - 1]
            target_rul = group.loc[target_idx, "RUL_hours"]
            
            start_time = group.loc[group_indices[i], "Timestamp"]
            end_time = group.loc[target_idx, "Timestamp"]
            
            sequences.append(seq_x)
            targets.append(target_rul)
            meta_vehicle_id.append(vehicle_id)
            meta_start_time.append(start_time)
            meta_end_time.append(end_time)
            meta_seq_id.append(f"{vehicle_id}_seq_{seq_counter}")
            seq_counter += 1
            
    return (
        np.array(sequences),
        np.array(targets),
        np.array(meta_vehicle_id),
        np.array(meta_start_time),
        np.array(meta_end_time),
        np.array(meta_seq_id)
    )

def main():
    print("Phase L/O-2: Prep Logistic/Officer LSTM Data")
    
    data_path = r"d:\VEDA\datasets\logistic_officer\raw\VEDA_Logistic_Officer_Fresh_RUL_Dataset.csv"
    splits_path = r"d:\VEDA\datasets\logistic_officer\raw\VEDA_Logistic_Officer_Vehicle_Splits.json"
    rf_dir = r"d:\VEDA\ml\logistic_officer\random_forest\VEDA_Logistic_Officer_RF_Phase1_Output"
    output_dir = r"d:\VEDA\datasets\logistic_officer\downstream"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading raw data and RF model...")
    df = pd.read_csv(data_path)
    
    # Sort strictly by Vehicle_ID and Timestamp
    df = df.sort_values(by=["Vehicle_ID", "Timestamp"]).reset_index(drop=True)
    
    with open(splits_path, 'r') as f:
        splits = json.load(f)
        
    with open(os.path.join(rf_dir, "RF_phase1_model.pkl"), "rb") as f:
        rf_model = pickle.load(f)
        
    with open(os.path.join(rf_dir, "RF_phase1_feature_columns.json"), "r") as f:
        rf_features = json.load(f)
        
    with open(os.path.join(rf_dir, "RF_phase1_risk_threshold.json"), "r") as f:
        threshold = json.load(f)["risk_threshold"]
        
    print("Generating RF inference features...")
    # Generate RF outputs for all rows
    X_rf = df[rf_features]
    rf_probs = rf_model.predict_proba(X_rf)[:, 1]
    rf_preds = (rf_probs >= threshold).astype(int)
    
    df["RF_Abnormal_Probability"] = rf_probs
    df["RF_Abnormal_Prediction"] = rf_preds
    
    print("Defining LSTM feature contract...")
    # LSTM Features = RF_features + RF outputs
    # Cat = Operating_Terrain (from RF features if exists)
    # Num = (RF_features - Cat) + [RF_Abnormal_Probability, RF_Abnormal_Prediction]
    cat_features = ["Operating_Terrain"] if "Operating_Terrain" in rf_features else []
    num_features = [f for f in rf_features if f not in cat_features] + ["RF_Abnormal_Probability", "RF_Abnormal_Prediction"]
    
    lstm_features = num_features + cat_features
    print(f"Total LSTM features: {len(lstm_features)}")
    
    # Preprocessor: scale numeric, encode categorical
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features)
        ]
    )
    
    # Fit only on train split
    train_vehicles = splits["train"]
    val_vehicles = splits["validation"]
    test_vehicles = splits["test"]
    
    train_mask = df["Vehicle_ID"].isin(train_vehicles)
    val_mask = df["Vehicle_ID"].isin(val_vehicles)
    test_mask = df["Vehicle_ID"].isin(test_vehicles)
    
    print("Fitting scaler on training data...")
    # Fit preprocessor on training data subset
    preprocessor.fit(df.loc[train_mask, lstm_features])
    
    # Transform all data to create feature matrix
    print("Transforming all data...")
    X_transformed = preprocessor.transform(df[lstm_features])
    
    # Get feature names for contract
    num_feature_names = num_features
    cat_out_features = []
    if len(cat_features) > 0:
        cat_enc = preprocessor.named_transformers_['cat']
        cat_out_features = cat_enc.get_feature_names_out(cat_features).tolist()
    final_feature_names = num_feature_names + cat_out_features
    
    # Save the scaler and feature names
    scaler_out_dir = r"d:\VEDA\ml\logistic_officer\lstm_1dcnn\VEDA_Logistic_Officer_LSTM_1DCNN_Phase2_Output"
    os.makedirs(scaler_out_dir, exist_ok=True)
    with open(os.path.join(scaler_out_dir, "feature_scaler_train_only.pkl"), "wb") as f:
        pickle.dump(preprocessor, f)
    with open(os.path.join(scaler_out_dir, "LSTM_1DCNN_phase2_feature_columns.json"), "w") as f:
        json.dump(final_feature_names, f, indent=4)
    with open(os.path.join(scaler_out_dir, "LSTM_1DCNN_phase2_feature_columns.pkl"), "wb") as f:
        pickle.dump(final_feature_names, f)
        
    print("Creating sequential NPZ datasets...")
    
    df_train = df[train_mask]
    df_val = df[val_mask]
    df_test = df[test_mask]
    
    def process_split(split_df, split_name):
        # the indices in split_df correspond to rows in the original df
        # but to slice X_transformed, we must use the original df index because X_transformed corresponds to df exactly
        
        X_seq, y_seq, meta_vid, meta_start, meta_end, meta_seqid = create_sequences(df, X_transformed, seq_length=30)
        
        # filter sequences belonging to this split's vehicles
        split_vehicles = split_df["Vehicle_ID"].unique()
        mask = np.isin(meta_vid, split_vehicles)
        
        out_npz = os.path.join(output_dir, f"downstream_{split_name}_lstm_1dcnn.npz")
        np.savez(
            out_npz,
            X=X_seq[mask],
            y=y_seq[mask],
            Vehicle_ID=meta_vid[mask],
            Start_Timestamp=meta_start[mask],
            End_Timestamp=meta_end[mask],
            Sequence_ID=meta_seqid[mask]
        )
        print(f"Saved {split_name} split to {out_npz}. Shape: {X_seq[mask].shape}")
        
    process_split(df_train, "train")
    process_split(df_val, "validation")
    process_split(df_test, "test")
    
    print("Prep complete.")

if __name__ == "__main__":
    main()
