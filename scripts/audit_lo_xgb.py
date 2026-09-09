import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from scipy.stats import pearsonr, spearmanr

def main():
    print("Starting L/O-3 Performance Audit (XGBoost)...")
    
    # Paths
    raw_data_path = r"d:\VEDA\datasets\logistic_officer\raw\VEDA_Logistic_Officer_Fresh_RUL_Dataset.csv"
    npz_dir = r"d:\VEDA\datasets\logistic_officer\downstream"
    xgb_dir = r"d:\VEDA\ml\logistic_officer\xgboost\VEDA_Logistic_Officer_XGB_Phase3_Output"
    audit_dir = r"d:\VEDA\ml\logistic_officer\xgboost\VEDA_Logistic_Officer_XGB_Performance_Audit"
    os.makedirs(audit_dir, exist_ok=True)
    
    # 1. Load Data
    print("Loading data...")
    df_raw = pd.read_csv(raw_data_path)
    
    train_npz = np.load(os.path.join(npz_dir, "downstream_train_lstm_1dcnn.npz"), allow_pickle=True)
    val_npz = np.load(os.path.join(npz_dir, "downstream_validation_lstm_1dcnn.npz"), allow_pickle=True)
    test_npz = np.load(os.path.join(npz_dir, "downstream_test_lstm_1dcnn.npz"), allow_pickle=True)
    
    X_train_orig, y_train = train_npz['X'], train_npz['y']
    X_val_orig, y_val = val_npz['X'], val_npz['y']
    X_test_orig, y_test = test_npz['X'], test_npz['y']
    
    X_train = X_train_orig.reshape(X_train_orig.shape[0], -1)
    X_val = X_val_orig.reshape(X_val_orig.shape[0], -1)
    X_test = X_test_orig.reshape(X_test_orig.shape[0], -1)
    
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
    
    # 3. Baseline Comparison
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
        
    # 4. Prediction Analysis
    print("Prediction Analysis...")
    model = XGBRegressor()
    model.load_model(os.path.join(xgb_dir, "VEDA_Logistic_Officer_XGB_Phase3_model.json"))
    
    pred_val = model.predict(X_val)
    pred_test = model.predict(X_test)
    
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
    
    # 5. Sensor/Feature -> RUL Relationship
    print("Sensor -> RUL Relationship...")
    # Use original 28 features (timestep 29) to avoid 840 correlations
    lstm_dir = r"d:\VEDA\ml\logistic_officer\lstm_1dcnn\VEDA_Logistic_Officer_LSTM_1DCNN_Phase2_Output"
    with open(os.path.join(lstm_dir, "LSTM_1DCNN_phase2_feature_columns.json"), 'r') as f:
        feature_cols = json.load(f)
        
    X_train_last = X_train_orig[:, -1, :] # (N, 28)
    corr_data = []
    for i, col_name in enumerate(feature_cols):
        feat = X_train_last[:, i]
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
    
    # 6. Feature Importance
    print("Feature Importance Analysis...")
    df_fi = pd.read_csv(os.path.join(xgb_dir, "phase3_xgb_feature_importance.csv"))
    df_fi.head(20).to_csv(os.path.join(audit_dir, "feature_importance_analysis.csv"), index=False)
    
    # 7. Vehicle-level Analysis
    print("Vehicle-level Analysis...")
    v_stats = []
    for vid in np.unique(test_vids):
        mask = (test_vids == vid)
        y_v = y_test[mask]
        p_v = pred_test[mask]
        v_stats.append({
            'Vehicle_ID': vid,
            'Count': len(y_v),
            'Actual_Mean': np.mean(y_v),
            'Pred_Mean': np.mean(p_v),
            'Actual_Range': np.max(y_v) - np.min(y_v),
            'Pred_Range': np.max(p_v) - np.min(p_v),
            'MAE': mean_absolute_error(y_v, p_v),
            'RMSE': np.sqrt(mean_squared_error(y_v, p_v)),
            'R2': r2_score(y_v, p_v)
        })
    pd.DataFrame(v_stats).to_csv(os.path.join(audit_dir, "per_vehicle_analysis.csv"), index=False)
    
    # 8. RUL Intercept Investigation
    print("RUL Intercept Investigation...")
    traj_data = []
    for split_name, vids, y_data in zip(['Train', 'Validation', 'Test'], [train_npz['Vehicle_ID'], val_npz['Vehicle_ID'], test_npz['Vehicle_ID']], [y_train, y_val, y_test]):
        for vid in np.unique(vids):
            mask = (vids == vid)
            y_v = y_data[mask]
            
            initial_rul = y_v[0]
            final_rul = y_v[-1]
            total_decline = initial_rul - final_rul
            # Slope per sequence step (assumes strictly ordered)
            slope = (final_rul - initial_rul) / (len(y_v) - 1) if len(y_v) > 1 else 0
            
            traj_data.append({
                'Split': split_name,
                'Vehicle_ID': vid,
                'Initial_RUL': initial_rul,
                'Final_RUL': final_rul,
                'Total_Decline': total_decline,
                'Slope_Per_Step': slope
            })
    pd.DataFrame(traj_data).to_csv(os.path.join(audit_dir, "vehicle_rul_trajectory_analysis.csv"), index=False)
    
    # 9. Flattening Audit
    print("Flattening Audit...")
    # Verify flattening preserves temporal order
    # (N, 30, 28) -> (N, 840)
    # The convention is [t0_f0, t0_f1, ..., t29_f27]
    sample_orig = X_train_orig[0]
    sample_flat = X_train[0]
    flat_matches = True
    idx = 0
    for t in range(30):
        for f in range(28):
            if sample_orig[t, f] != sample_flat[idx]:
                flat_matches = False
            idx += 1
            
    with open(os.path.join(audit_dir, "flattening_audit.json"), 'w') as f:
        json.dump({'Flattening_Preserves_Order': flat_matches}, f, indent=4)
        
    # 10. Target Alignment Audit
    print("Sequence/Target Alignment...")
    align_results = []
    for i in np.random.choice(len(y_test), 5, replace=False):
        vid = test_npz['Vehicle_ID'][i]
        end_t = test_npz['End_Timestamp'][i]
        target_rul = test_npz['y'][i]
        
        v_df = df_raw[df_raw['Vehicle_ID'] == vid].sort_values('Timestamp').reset_index(drop=True)
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
