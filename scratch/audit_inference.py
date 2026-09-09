import sys
import os
import joblib
import pandas as pd
import numpy as np

def audit_tank():
    print("--- TANK ML AUDIT ---")
    try:
        rf_path = "ml/tank/random_forest/VEDA_Tank_RF_Phase4_Output/RF_phase4_model.pkl"
        if os.path.exists(rf_path):
            rf_model = joblib.load(rf_path)
            print("Tank RF Loaded.")
        else:
            print("Tank RF model not found.")
            
    except Exception as e:
        print(f"Tank RF Load Failed: {e}")

def audit_lo():
    print("--- LOGISTIC/OFFICER ML AUDIT ---")
    try:
        rf_path = "ml/logistic_officer/random_forest/VEDA_Logistic_Officer_RF_Phase1_V2_Output/RF_phase1_v2_model.pkl"
        if os.path.exists(rf_path):
            rf_model = joblib.load(rf_path)
            print("LO RF V2 Loaded.")
        else:
            print("LO RF V2 model not found.")
            
    except Exception as e:
        print(f"LO RF Load Failed: {e}")

if __name__ == "__main__":
    audit_tank()
    audit_lo()
