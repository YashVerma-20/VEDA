import os
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr

def investigate():
    dataset_dir = r"d:\VEDA\datasets\logistic_officer\corrected_rul"
    csv_path = os.path.join(dataset_dir, "VEDA_Logistic_Officer_Corrected_RUL_Dataset.csv")
    
    df = pd.read_csv(csv_path)
    
    print("======================================")
    print("2. PER-VEHICLE RUL STATISTICS")
    vids = df['Vehicle_ID'].unique()
    
    stats = []
    
    for vid in vids:
        v_df = df[df['Vehicle_ID'] == vid].sort_values('Timestamp').reset_index(drop=True)
        ruls = v_df['RUL_hours'].values
        healths = v_df['Health_Index'].values
        
        initial_h = healths[0]
        final_h = healths[-1]
        deg_rate = (healths[0] - healths[-1]) / len(healths)
        
        initial_rul = ruls[0]
        final_rul = ruls[-1]
        
        # approximate EOL time
        # EOL is when rul = 0
        
        start_t = pd.to_datetime(v_df['Timestamp'].iloc[0])
        end_t = pd.to_datetime(v_df['Timestamp'].iloc[-1])
        
        # since rul drops to 0 at the end exactly, EOL_time is end_t
        
        stats.append({
            'Vehicle_ID': vid,
            'Vehicle_Class': v_df['Vehicle_Class'].iloc[0],
            'Initial_H': initial_h,
            'Final_H': final_h,
            'Deg_Rate': deg_rate,
            'Initial_RUL': initial_rul,
            'Final_RUL': final_rul,
            'RUL_Range': initial_rul - final_rul,
            'Mean_RUL': np.mean(ruls)
        })
    
    df_stats = pd.DataFrame(stats)
    print(df_stats.head())
    
    print("\n======================================")
    print("3. TEST FOR UNIVERSAL RUL")
    print(f"std(initial_RUL): {df_stats['Initial_RUL'].std()}")
    print(f"std(final_RUL): {df_stats['Final_RUL'].std()}")
    print(f"std(mean_RUL): {df_stats['Mean_RUL'].std()}")
    
    print("\n======================================")
    print("4. TEST THE DEGRADATION <-> RUL CONNECTION")
    print("corr(degradation_rate, initial_RUL):", pearsonr(df_stats['Deg_Rate'], df_stats['Initial_RUL'])[0])
    print("corr(initial Health, initial_RUL):", pearsonr(df_stats['Initial_H'], df_stats['Initial_RUL'])[0])
    
if __name__ == "__main__":
    investigate()
