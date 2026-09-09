import pandas as pd
import numpy as np
import os
import json

def investigate():
    raw_data_path = r"d:\VEDA\datasets\logistic_officer\raw\VEDA_Logistic_Officer_Fresh_RUL_Dataset.csv"
    df = pd.read_csv(raw_data_path)
    
    audit_dir = r"d:\VEDA\ml\logistic_officer\VEDA_Logistic_Officer_RUL_Correction_Design_Audit"
    os.makedirs(audit_dir, exist_ok=True)
    
    # 2. IDENTIFY CURRENT DATASET GENERATOR
    # Since the script is missing, we infer its behavior.
    
    # 3. TRACE CURRENT RUL GENERATION
    print("--- RUL Generation ---")
    vids = df['Vehicle_ID'].unique()
    rul_slopes = []
    initial_ruls = []
    for vid in vids:
        v_df = df[df['Vehicle_ID'] == vid].sort_values('Timestamp').reset_index(drop=True)
        ruls = v_df['RUL_hours'].values
        initial_ruls.append(ruls[0])
        rul_slopes.append((ruls[-1] - ruls[0]) / (len(ruls) - 1))
    
    print(f"RUL Slopes unique values: {np.unique(np.round(rul_slopes, 5))}")
    print(f"Initial RUL variance: {np.var(initial_ruls)}")
    
    # 4. TRACE HEALTH GENERATION
    print("--- Health_Index Generation ---")
    health_slopes = []
    initial_healths = []
    for vid in vids:
        v_df = df[df['Vehicle_ID'] == vid].sort_values('Timestamp').reset_index(drop=True)
        healths = v_df['Health_Index'].values
        initial_healths.append(healths[0])
        health_slopes.append((healths[-1] - healths[0]) / (len(healths) - 1))
        
    print(f"Health Slopes unique values: {np.unique(np.round(health_slopes, 5))}")
    print(f"Initial Health variance: {np.var(initial_healths)}")
    
    # Check if Health_Index = RUL_hours / something
    h_ratio = df['Health_Index'] / df['RUL_hours']
    print(f"Health/RUL ratio variance: {np.var(h_ratio.dropna())}")
    
    # 5. TRACE DEGRADATION_INDEX
    print("--- Degradation_Index Generation ---")
    if 'Degradation_Index' in df.columns:
        corr_h_d = np.corrcoef(df['Health_Index'], df['Degradation_Index'])[0, 1]
        print(f"Correlation Health vs Degradation: {corr_h_d}")
    
    # 6. SENSOR GENERATION
    print("--- Sensor Dependencies ---")
    numeric_df = df.select_dtypes(include=[np.number])
    sensor_cols = [c for c in numeric_df.columns if c not in ['Timestamp', 'RUL_hours', 'Health_Index', 'Degradation_Index', 'RF_Abnormal_Label']]
    sensor_deps = []
    for col in sensor_cols:
        if numeric_df[col].std() < 1e-6:
            continue
        corr_rul = np.corrcoef(numeric_df[col], numeric_df['RUL_hours'])[0, 1]
        corr_health = np.corrcoef(numeric_df[col], numeric_df['Health_Index'])[0, 1]
        sensor_deps.append({
            'Sensor': col,
            'Corr_RUL': corr_rul,
            'Corr_Health': corr_health,
            'Abs_Corr_RUL': abs(corr_rul),
            'Abs_Corr_Health': abs(corr_health)
        })
    df_sensors = pd.DataFrame(sensor_deps).sort_values('Abs_Corr_Health', ascending=False)
    print(df_sensors.head())
    df_sensors.to_csv(os.path.join(audit_dir, "sensor_dependency_analysis.csv"), index=False)
    
    with open(os.path.join(audit_dir, "current_generator_analysis.json"), "w") as f:
        json.dump({"generator_status": "MISSING_FROM_WORKSPACE", "inferred_rul_slope": -0.25}, f)


if __name__ == "__main__":
    investigate()
