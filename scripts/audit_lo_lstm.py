import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from scipy.stats import pearsonr, spearmanr

def main():
    print("Starting L/O-2 Performance Audit...")
    
    # Paths
    raw_data_path = r"d:\VEDA\datasets\logistic_officer\raw\VEDA_Logistic_Officer_Fresh_RUL_Dataset.csv"
    splits_path = r"d:\VEDA\datasets\logistic_officer\raw\VEDA_Logistic_Officer_Vehicle_Splits.json"
    npz_dir = r"d:\VEDA\datasets\logistic_officer\downstream"
    lstm_dir = r"d:\VEDA\ml\logistic_officer\lstm_1dcnn\VEDA_Logistic_Officer_LSTM_1DCNN_Phase2_Output"
    audit_dir = r"d:\VEDA\ml\logistic_officer\lstm_1dcnn\VEDA_Logistic_Officer_LSTM_1DCNN_Performance_Audit"
    os.makedirs(audit_dir, exist_ok=True)
    
    # 1. Load Data
    print("Loading data...")
    df_raw = pd.read_csv(raw_data_path)
    with open(splits_path, 'r') as f:
        splits = json.load(f)
        
    train_npz = np.load(os.path.join(npz_dir, "downstream_train_lstm_1dcnn.npz"), allow_pickle=True)
    val_npz = np.load(os.path.join(npz_dir, "downstream_validation_lstm_1dcnn.npz"), allow_pickle=True)
    test_npz = np.load(os.path.join(npz_dir, "downstream_test_lstm_1dcnn.npz"), allow_pickle=True)
    
    X_train, y_train = train_npz['X'], train_npz['y']
    X_val, y_val = val_npz['X'], val_npz['y']
    X_test, y_test = test_npz['X'], test_npz['y']
    
    train_vids = train_npz['Vehicle_ID']
    val_vids = val_npz['Vehicle_ID']
    test_vids = test_npz['Vehicle_ID']
    
    # 2. RUL Distribution Audit
    print("RUL Distribution Audit...")
    dist_stats = []
    for split_name, y_data in zip(['Train', 'Validation', 'Test'], [y_train, y_val, y_test]):
        dist_stats.append({
            'Split': split_name,
            'Count': len(y_data),
            'Min': np.min(y_data),
            'Max': np.max(y_data),
            'Mean': np.mean(y_data),
            'Median': np.median(y_data),
            'Std': np.std(y_data),
            'Var': np.var(y_data),
            '25th': np.percentile(y_data, 25),
            '75th': np.percentile(y_data, 75)
        })
    pd.DataFrame(dist_stats).to_csv(os.path.join(audit_dir, "distribution_analysis.csv"), index=False)
    
    # 3. RUL vs Time Audit
    print("RUL vs Time Audit...")
    rep_vids = {
        'Train': splits['train'][0],
        'Validation': splits['validation'][0],
        'Test': splits['test'][0]
    }
    for split_name, vid in rep_vids.items():
        v_df = df_raw[df_raw['Vehicle_ID'] == vid].sort_values('Timestamp')
        plt.figure(figsize=(10, 5))
        plt.plot(v_df['Timestamp'], v_df['RUL_hours'], marker='.')
        plt.title(f"RUL vs Time: {vid} ({split_name})")
        plt.xlabel("Timestamp")
        plt.ylabel("RUL_hours")
        plt.savefig(os.path.join(audit_dir, f"rul_vs_time_{split_name}_{vid}.png"))
        plt.close()
        
    # 4. Sensor -> RUL Relationship
    print("Sensor -> RUL Relationship...")
    with open(os.path.join(lstm_dir, "LSTM_1DCNN_phase2_feature_columns.json"), 'r') as f:
        feature_cols = json.load(f)
        
    # Reconstruct raw dataframe with same features if possible. 
    # RF features might not be in raw dataset. Let's compute them or skip.
    # Actually, we can use the flattened X_train or just the last timestep of X_train to compute correlation with y_train.
    # X_train is scaled, which doesn't affect correlation.
    X_train_last = X_train[:, -1, :] # (N, 28)
    corr_data = []
    for i, col_name in enumerate(feature_cols):
        feat = X_train_last[:, i]
        # Handle constant features
        if np.std(feat) < 1e-6:
            p_corr, s_corr = 0, 0
        else:
            p_corr, _ = pearsonr(feat, y_train)
            s_corr, _ = spearmanr(feat, y_train)
        corr_data.append({
            'Feature': col_name,
            'Pearson': p_corr,
            'Spearman': s_corr,
            'Abs_Spearman': abs(s_corr)
        })
    df_corr = pd.DataFrame(corr_data).sort_values('Abs_Spearman', ascending=False)
    df_corr.to_csv(os.path.join(audit_dir, "correlation_analysis.csv"), index=False)
    
    # 5. Vehicle-level Analysis
    print("Vehicle-level Analysis...")
    v_stats = []
    for vid in np.unique(test_vids):
        mask = (test_vids == vid)
        y_v = y_test[mask]
        v_stats.append({
            'Vehicle_ID': vid,
            'Count': len(y_v),
            'Min': np.min(y_v),
            'Max': np.max(y_v),
            'Mean': np.mean(y_v),
            'Range': np.max(y_v) - np.min(y_v)
        })
    pd.DataFrame(v_stats).to_csv(os.path.join(audit_dir, "per_vehicle_analysis.csv"), index=False)
    
    # 6. Baseline Comparison
    print("Baseline Comparison...")
    mean_rul = np.mean(y_train)
    
    val_baseline_pred = np.full_like(y_val, mean_rul)
    test_baseline_pred = np.full_like(y_test, mean_rul)
    
    baselines = {
        'Validation_MeanBaseline': {
            'MAE': mean_absolute_error(y_val, val_baseline_pred),
            'RMSE': np.sqrt(mean_squared_error(y_val, val_baseline_pred)),
            'R2': r2_score(y_val, val_baseline_pred)
        },
        'Test_MeanBaseline': {
            'MAE': mean_absolute_error(y_test, test_baseline_pred),
            'RMSE': np.sqrt(mean_squared_error(y_test, test_baseline_pred)),
            'R2': r2_score(y_test, test_baseline_pred)
        }
    }
    with open(os.path.join(audit_dir, "baseline_metrics.json"), 'w') as f:
        json.dump(baselines, f, indent=4)
        
    # 7. Prediction Analysis
    print("Prediction Analysis...")
    model = load_model(os.path.join(lstm_dir, "VEDA_Logistic_Officer_LSTM_1DCNN_final.keras"))
    pred_val = model.predict(X_val).flatten()
    pred_test = model.predict(X_test).flatten()
    
    pred_stats = []
    for split_name, y_true, y_pred in zip(['Validation', 'Test'], [y_val, y_test], [pred_val, pred_test]):
        pred_stats.append({
            'Split': split_name,
            'Actual_Mean': np.mean(y_true),
            'Actual_Std': np.std(y_true),
            'Pred_Mean': np.mean(y_pred),
            'Pred_Std': np.std(y_pred),
            'Std_Ratio': np.std(y_pred) / np.std(y_true),
            'MAE': mean_absolute_error(y_true, y_pred),
            'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
            'R2': r2_score(y_true, y_pred)
        })
        
        # Plots
        plt.figure(figsize=(8,8))
        plt.scatter(y_true, y_pred, alpha=0.1)
        plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--')
        plt.xlabel('Actual RUL')
        plt.ylabel('Predicted RUL')
        plt.title(f'Actual vs Predicted ({split_name})')
        plt.savefig(os.path.join(audit_dir, f"actual_vs_predicted_{split_name}.png"))
        plt.close()
        
        plt.figure(figsize=(8,8))
        plt.scatter(y_true, y_pred - y_true, alpha=0.1)
        plt.axhline(0, color='r', linestyle='--')
        plt.xlabel('Actual RUL')
        plt.ylabel('Residual (Pred - Actual)')
        plt.title(f'Residual Plot ({split_name})')
        plt.savefig(os.path.join(audit_dir, f"residual_plot_{split_name}.png"))
        plt.close()
        
        plt.figure(figsize=(10,5))
        plt.hist(y_true, bins=50, alpha=0.5, label='Actual')
        plt.hist(y_pred, bins=50, alpha=0.5, label='Predicted')
        plt.legend()
        plt.title(f'Distribution ({split_name})')
        plt.savefig(os.path.join(audit_dir, f"distribution_plot_{split_name}.png"))
        plt.close()
        
    pd.DataFrame(pred_stats).to_csv(os.path.join(audit_dir, "prediction_analysis.csv"), index=False)
    
    # 8. Sequence/Target Alignment
    print("Sequence/Target Alignment...")
    align_results = []
    # Test random sequences
    for i in np.random.choice(len(y_test), 5, replace=False):
        vid = test_npz['Vehicle_ID'][i]
        start_t = test_npz['Start_Timestamp'][i]
        end_t = test_npz['End_Timestamp'][i]
        target_rul = test_npz['y'][i]
        
        # Verify in raw data
        v_df = df_raw[df_raw['Vehicle_ID'] == vid].sort_values('Timestamp').reset_index(drop=True)
        # Find endpoint
        end_row = v_df[v_df['Timestamp'] == end_t]
        if not end_row.empty:
            actual_rul = end_row['RUL_hours'].values[0]
            align_results.append({
                'Index': int(i),
                'Vehicle': str(vid),
                'End_Timestamp': str(end_t),
                'Target_RUL_in_NPZ': float(target_rul),
                'Actual_RUL_in_Raw': float(actual_rul),
                'Match': bool(abs(target_rul - actual_rul) < 1e-4)
            })
    with open(os.path.join(audit_dir, "alignment_audit.json"), 'w') as f:
        json.dump(align_results, f, indent=4)
        
    print("Audit calculations complete.")

if __name__ == "__main__":
    main()
