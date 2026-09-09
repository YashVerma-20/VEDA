import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from scipy.stats import pearsonr, spearmanr

def validate():
    print("Starting L/O Corrected Dataset V2 Validation...")
    
    dataset_dir = r"d:\VEDA\datasets\logistic_officer\corrected_rul_v2"
    csv_path = os.path.join(dataset_dir, "VEDA_Logistic_Officer_Corrected_RUL_Dataset.csv")
    splits_path = os.path.join(dataset_dir, "VEDA_Logistic_Officer_Corrected_RUL_Vehicle_Splits.json")
    val_dir = r"d:\VEDA\ml\logistic_officer\VEDA_Logistic_Officer_Corrected_RUL_V2_Validation"
    
    os.makedirs(val_dir, exist_ok=True)
    
    df = pd.read_csv(csv_path)
    with open(splits_path, 'r') as f:
        splits = json.load(f)
        
    errors = []
    
    # Gates
    vids = df['Vehicle_ID'].unique()
    logistics_count = len(df[df['Vehicle_Class'] == 'Logistic Truck']['Vehicle_ID'].unique())
    officer_count = len(df[df['Vehicle_Class'] == 'Officer Vehicle']['Vehicle_ID'].unique())
    
    if len(vids) != 40: errors.append(f"A: Vehicles count is {len(vids)}, expected 40")
    if logistics_count != 20 or officer_count != 20: errors.append("B: Logistic/Officer count is not 20/20")
    
    counts_per_vid = df.groupby('Vehicle_ID').size()
    if not (counts_per_vid == 1000).all(): errors.append("C: Not exactly 1000 obs per vehicle")
    
    train_v = splits['train']
    val_v = splits['validation']
    test_v = splits['test']
    
    if len(set(train_v) & set(val_v)) > 0 or len(set(train_v) & set(test_v)) > 0:
        errors.append("E: Train/Validation/Test not disjoint")
    if len(train_v) != 24 or len(val_v) != 8 or len(test_v) != 8:
        errors.append("F: Split counts not 24/8/8")
        
    if df.duplicated().any(): errors.append("H: Duplicate rows found")
    if df.isnull().any().any(): errors.append("I: Missing values found")
    if np.isinf(df.select_dtypes(include=[np.number])).any().any(): errors.append("J: Infinite values found")
    
    if 'RUL_hours' not in df.columns: errors.append("K: RUL_hours absent")
    elif (df['RUL_hours'] < 0).any(): errors.append("L: RUL_hours has negative values")
    
    if 'RF_Abnormal_Probability' in df.columns: errors.append("M: RF_Abnormal_Probability present")
    if 'RF_Abnormal_Prediction' in df.columns: errors.append("N: RF_Abnormal_Prediction present")
    
    # Trajectory Gates
    print("Running Trajectory Gates...")
    traj_data = []
    slopes = []
    initial_ruls = []
    mean_ruls = []
    eol_times = []
    for vid in vids:
        v_df = df[df['Vehicle_ID'] == vid].sort_values('Timestamp').reset_index(drop=True)
        ruls = v_df['RUL_hours'].values
        initial = ruls[0]
        final = ruls[-1]
        slope = (final - initial) / (len(ruls) - 1)
        mean_rul = np.mean(ruls)
        
        slopes.append(slope)
        initial_ruls.append(initial)
        mean_ruls.append(mean_rul)
        
        # EOL time is the timestamp plus final RUL
        # or since RUL = lifetime_hours - current_t, EOL_time is fixed per vehicle
        eol_time = pd.to_datetime(v_df['Timestamp'].iloc[-1]) + pd.Timedelta(hours=final)
        eol_times.append(eol_time)
        
        traj_data.append({
            'Vehicle_ID': vid,
            'Initial_RUL': initial,
            'Final_RUL': final,
            'Decline': initial - final,
            'Slope_Per_Step': slope,
            'Mean_RUL': mean_rul
        })
    df_traj = pd.DataFrame(traj_data)
    df_traj.to_csv(os.path.join(val_dir, "vehicle_rul_trajectory.csv"), index=False)
    
    # UNIVERSAL COUNTDOWN TEST
    if np.std(initial_ruls) < 1e-5: errors.append("UNIVERSAL COUNTDOWN: Initial RUL does not vary")
    if np.std(mean_ruls) < 1e-5: errors.append("UNIVERSAL COUNTDOWN: Mean RUL does not vary")
    
    if np.abs(initial_ruls[0] - 249.75) < 1e-3 and np.std(initial_ruls) < 1e-3:
        errors.append("UNIVERSAL COUNTDOWN: initial_RUL == 249.75 for every vehicle")
    if np.abs(mean_ruls[0] - 124.875) < 1e-3 and np.std(mean_ruls) < 1e-3:
        errors.append("UNIVERSAL COUNTDOWN: mean_RUL == 124.875 for every vehicle")

    print("Running Sensor Corrs...")
    sensor_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in ['Timestamp_Hour', 'Timestamp_DayOfWeek', 'Timestamp_Month', 'RUL_hours', 'Health_Index', 'Degradation_Index', 'RF_Abnormal_Label']]
    
    corrs = []
    sh_corrs = []
    for col in sensor_cols:
        if df[col].std() > 1e-6:
            s_corr = spearmanr(df[col], df['RUL_hours'])[0]
            corrs.append({'Sensor': col, 'Spearman': s_corr, 'Abs_Spearman': abs(s_corr)})
            
            s_corr_h = spearmanr(df[col], df['Health_Index'])[0]
            sh_corrs.append({'Sensor': col, 'Spearman': s_corr_h, 'Abs_Spearman': abs(s_corr_h)})
            
    df_corr = pd.DataFrame(corrs).sort_values('Abs_Spearman', ascending=False)
    df_corr.to_csv(os.path.join(val_dir, "sensor_rul_correlations.csv"), index=False)
    df_sh = pd.DataFrame(sh_corrs).sort_values('Abs_Spearman', ascending=False)
    df_sh.to_csv(os.path.join(val_dir, "sensor_health_correlations.csv"), index=False)
    
    print("Running Baseline Eval...")
    df_train = df[df['Vehicle_ID'].isin(train_v)]
    df_val = df[df['Vehicle_ID'].isin(val_v)]
    df_test = df[df['Vehicle_ID'].isin(test_v)]
    
    train_mean = df_train['RUL_hours'].mean()
    val_pred = np.full(len(df_val), train_mean)
    test_pred = np.full(len(df_test), test_pred_mean := train_mean)
    
    baselines = {
        "Validation_MeanBaseline": {
            "MAE": mean_absolute_error(df_val['RUL_hours'], val_pred),
            "RMSE": np.sqrt(mean_squared_error(df_val['RUL_hours'], val_pred))
        },
        "Test_MeanBaseline": {
            "MAE": mean_absolute_error(df_test['RUL_hours'], test_pred),
            "RMSE": np.sqrt(mean_squared_error(df_test['RUL_hours'], test_pred))
        }
    }
    with open(os.path.join(val_dir, "baseline_metrics.json"), "w") as f:
        json.dump(baselines, f, indent=4)
        
    df['RUL_hours'].describe().to_csv(os.path.join(val_dir, "rul_distribution.csv"))
    fm_dist = df.groupby('Abnormal_Pattern').size().reset_index(name='count')
    fm_dist.to_csv(os.path.join(val_dir, "failure_mode_distribution.csv"), index=False)
    
    print(f"Hard gates passed: {len(errors) == 0}")
    if errors:
        for e in errors: print(e)
        
    with open(os.path.join(val_dir, "dataset_quality_report.json"), "w") as f:
        json.dump({"status": "PASS" if not errors else "FAIL", "errors": errors}, f, indent=4)
        
    # Output to stdout for final report reading
    print("----- METRICS FOR FINAL REPORT -----")
    print(f"std(initial_RUL): {np.std(initial_ruls)}")
    print(f"std(mean_RUL): {np.std(mean_ruls)}")
    print(f"Train Mean RUL: {df_train['RUL_hours'].mean()}")
    print(f"Validation Mean RUL: {df_val['RUL_hours'].mean()}")
    print(f"Test Mean RUL: {df_test['RUL_hours'].mean()}")
    print(f"Validation Baseline MAE: {baselines['Validation_MeanBaseline']['MAE']}")
    print(f"Test Baseline MAE: {baselines['Test_MeanBaseline']['MAE']}")
    
if __name__ == "__main__":
    validate()
