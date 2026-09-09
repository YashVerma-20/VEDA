import os
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr

def run_audit():
    dataset_dir = r"d:\VEDA\datasets\logistic_officer\corrected_rul"
    csv_path = os.path.join(dataset_dir, "VEDA_Logistic_Officer_Corrected_RUL_Dataset.csv")
    splits_path = os.path.join(dataset_dir, "VEDA_Logistic_Officer_Corrected_RUL_Vehicle_Splits.json")
    val_dir = r"d:\VEDA\ml\logistic_officer\VEDA_Logistic_Officer_Corrected_RUL_Validation"
    raw_csv = r"d:\VEDA\datasets\logistic_officer\raw\VEDA_Logistic_Officer_Fresh_RUL_Dataset.csv"
    
    print("======================================")
    print("AUDIT 1 - COLUMN CONTRACT")
    df = pd.read_csv(csv_path)
    old_df = pd.read_csv(raw_csv)
    new_cols = list(df.columns)
    old_cols = list(old_df.columns)
    print(f"Corrected columns ({len(new_cols)}):", new_cols)
    print(f"Old columns ({len(old_cols)}):", old_cols)
    print("Missing from old:", set(old_cols) - set(new_cols))
    print("New in corrected:", set(new_cols) - set(old_cols))
    
    print("\n======================================")
    print("AUDIT 2 - EXACT CLASS COUNTS")
    c = df['RF_Abnormal_Label'].value_counts()
    normal = c.get(0, 0)
    abnormal = c.get(1, 0)
    print(f"Normal: {normal} ({normal/len(df)*100}%)")
    print(f"Abnormal: {abnormal} ({abnormal/len(df)*100}%)")
    
    print("\n======================================")
    print("AUDIT 3 - RUL TRAJECTORY")
    vids = df['Vehicle_ID'].unique()
    slopes = []
    deg_rates = []
    r2_fits = []
    for vid in vids:
        v_df = df[df['Vehicle_ID'] == vid].sort_values('Timestamp').reset_index(drop=True)
        ruls = v_df['RUL_hours'].values
        healths = v_df['Health_Index'].values
        x = np.arange(len(ruls))
        fit = np.polyfit(x, ruls, 1)
        r2 = np.corrcoef(x, ruls)[0, 1] ** 2
        slopes.append(fit[0])
        r2_fits.append(r2)
        deg_rates.append((healths[0] - healths[-1]) / len(healths))
        
    print(f"Unique RUL slopes: {np.unique(np.round(slopes, 5))}")
    print(f"R2 of linear fits: Mean {np.mean(r2_fits)}, Min {np.min(r2_fits)}")
    print(f"Degradation rates: Min {np.min(deg_rates):.6f}, Max {np.max(deg_rates):.6f}, Mean {np.mean(deg_rates):.6f}, Std {np.std(deg_rates):.6f}")
    print(f"Unique deg rates: {len(np.unique(np.round(deg_rates, 6)))}")
    
    print("\n======================================")
    print("AUDIT 4 - SENSOR CORRELATIONS")
    sensor_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in ['Timestamp_Hour', 'Timestamp_DayOfWeek', 'Timestamp_Month', 'RUL_hours', 'Health_Index', 'Degradation_Index', 'RF_Abnormal_Label']]
    
    corrs = []
    for col in sensor_cols:
        if df[col].std() > 1e-6:
            s_rul = spearmanr(df[col], df['RUL_hours'])[0]
            s_health = spearmanr(df[col], df['Health_Index'])[0]
            corrs.append({'Sensor': col, 'Sp_RUL': s_rul, 'Sp_Health': s_health, 'Abs_Sp_RUL': abs(s_rul), 'Abs_Sp_Health': abs(s_health)})
    df_c = pd.DataFrame(corrs)
    print("Top 10 vs RUL:")
    print(df_c.sort_values('Abs_Sp_RUL', ascending=False).head(10)[['Sensor', 'Sp_RUL', 'Abs_Sp_RUL']])
    print("\nTop 10 vs Health:")
    print(df_c.sort_values('Abs_Sp_Health', ascending=False).head(10)[['Sensor', 'Sp_Health', 'Abs_Sp_Health']])
    
    print("\n======================================")
    print("AUDIT 6 - FAILURE MODE ANALYSIS")
    fm_counts = df.groupby(['Abnormal_Pattern', 'Affected_Sensors']).size().reset_index(name='count')
    print(fm_counts)
    
    print("\n======================================")
    print("AUDIT 7 - CLASSIFICATION SHORTCUTS")
    print("Mean RUL by Class:")
    print(df.groupby('Vehicle_Class')['RUL_hours'].mean())
    print("\nMean RUL by Terrain:")
    print(df.groupby('Operating_Terrain')['RUL_hours'].mean())
    print("\nAbnormal % by Class:")
    print(df.groupby('Vehicle_Class')['RF_Abnormal_Label'].mean())
    
    print("\n======================================")
    print("AUDIT 8 - MEAN-RUL BASELINE")
    with open(splits_path, 'r') as f:
        splits = json.load(f)
    print("Train Mean RUL:", df[df['Vehicle_ID'].isin(splits['train'])]['RUL_hours'].mean(), "Std:", df[df['Vehicle_ID'].isin(splits['train'])]['RUL_hours'].std())
    print("Val Mean RUL:", df[df['Vehicle_ID'].isin(splits['validation'])]['RUL_hours'].mean(), "Std:", df[df['Vehicle_ID'].isin(splits['validation'])]['RUL_hours'].std())
    print("Test Mean RUL:", df[df['Vehicle_ID'].isin(splits['test'])]['RUL_hours'].mean(), "Std:", df[df['Vehicle_ID'].isin(splits['test'])]['RUL_hours'].std())
    
    with open(os.path.join(val_dir, "baseline_metrics.json"), 'r') as f:
        print("Baseline Metrics:", json.dumps(json.load(f), indent=2))
        
if __name__ == "__main__":
    run_audit()
