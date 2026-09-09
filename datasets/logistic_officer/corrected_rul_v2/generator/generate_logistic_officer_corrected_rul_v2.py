import os
import json
import numpy as np
import pandas as pd

def generate_dataset():
    np.random.seed(20260903) # New fixed seed for reproducibility
    
    out_dir = r"d:\VEDA\datasets\logistic_officer\corrected_rul_v2"
    gen_dir = os.path.join(out_dir, "generator")
    os.makedirs(gen_dir, exist_ok=True)
    
    n_logistics = 20
    n_officer = 20
    n_vehicles = n_logistics + n_officer
    obs_per_vehicle = 1000
    interval_hours = 0.25
    eol_threshold = 0.15
    
    data = []
    
    for v_idx in range(n_vehicles):
        is_logistic = (v_idx < n_logistics)
        v_id = f"LOV_{str(v_idx+1).zfill(3)}"
        v_class = "Logistic Truck" if is_logistic else "Officer Vehicle"
        v_name = f"{v_class} Alpha-{v_idx+1}"
        
        terrain_opts = ['Desert', 'Mountain', 'Urban', 'Jungle', 'Arctic']
        v_terrain = np.random.choice(terrain_opts)
        
        # Vehicle-specific parameters
        # Ensure lifetime_hours is strictly > 250
        lifetime_hours = np.random.uniform(300, 1200)
        
        # Randomly sample the start time of the observation window
        # The window must end before or exactly at EOL (lifetime_hours)
        # 1000 observations = 249.75 hours elapsed from step 0 to step 999.
        # So maximum start_time is lifetime_hours - 249.75
        max_start_time = lifetime_hours - 249.75
        start_time = np.random.uniform(0, max_start_time)
        
        initial_health_global = 1.0
        health_slope = (1.0 - eol_threshold) / lifetime_hours
        
        failure_modes = ['Thermal', 'Mechanical', 'Electrical']
        f_mode = np.random.choice(failure_modes)
        
        base_timestamp = pd.Timestamp("2025-01-01 00:00:00") + pd.Timedelta(days=np.random.randint(0, 100))
        
        for step in range(obs_per_vehicle):
            t_hours = start_time + step * interval_hours
            current_time = base_timestamp + pd.Timedelta(hours=t_hours)
            
            health = initial_health_global - health_slope * t_hours
            rul = lifetime_hours - t_hours
            deg_idx = 1.0 - health
            
            speed = np.abs(np.sin(t_hours / 2.0)) * (80 if is_logistic else 120) + np.random.normal(0, 5)
            engine_rpm = speed * 25 + np.random.normal(800, 100)
            engine_load = np.clip(np.abs(np.sin(t_hours / 4.0)) * 100 + np.random.normal(0, 10), 0, 100)
            throttle = np.clip(engine_load + np.random.normal(0, 5), 0, 100)
            
            vibration = 2.0 + (5.0 * deg_idx) + np.random.normal(0, 0.5)
            if f_mode == 'Mechanical': vibration += (2.0 * deg_idx)
            
            brake_wear = 10.0 + (80.0 * deg_idx) + np.random.normal(0, 1.0)
            oil_pressure = 60.0 - (20.0 * deg_idx) + np.random.normal(0, 2.0)
            
            exhaust_temp = 300.0 + (150.0 * deg_idx) + engine_load * 2.0 + np.random.normal(0, 10)
            if f_mode == 'Thermal': exhaust_temp += (50.0 * deg_idx)
            
            trans_oil_temp = 80.0 + (40.0 * deg_idx) + np.random.normal(0, 3)
            
            battery = 14.0 - (2.0 * deg_idx) + np.random.normal(0, 0.1)
            if f_mode == 'Electrical': battery -= (1.0 * deg_idx)
            
            ambient = 25.0 + 10.0 * np.sin(t_hours / 12.0) + np.random.normal(0, 2)
            if v_terrain == 'Desert': ambient += 15.0
            elif v_terrain == 'Arctic': ambient -= 30.0
            
            intake_temp = ambient + engine_load * 0.1 + np.random.normal(0, 2)
            coolant_temp = 90.0 + engine_load * 0.2 + (10.0 * deg_idx) + np.random.normal(0, 2)
            oil_temp = coolant_temp + 10.0 + np.random.normal(0, 2)
            turbo_boost = engine_load * 0.2 + np.random.normal(0, 1)
            fuel = 100.0 - ((t_hours % 10) * 10) + np.random.normal(0, 1)
            tire_pressure = 32.0 - (5.0 * deg_idx) + np.random.normal(0, 0.5)
            odometer = 10000 + t_hours * 40.0
            
            row = {
                "Vehicle_ID": v_id,
                "Vehicle_Name": v_name,
                "Vehicle_Class": v_class,
                "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Operating_Terrain": v_terrain,
                "Odometer_km": odometer,
                "Engine_RPM": engine_rpm,
                "Speed_kmph": speed,
                "Coolant_Temp_C": coolant_temp,
                "Oil_Temp_C": oil_temp,
                "Oil_Pressure_bar": oil_pressure,
                "Fuel_Level_pct": fuel,
                "Battery_Voltage_V": battery,
                "Engine_Load_pct": engine_load,
                "Throttle_Position_pct": throttle,
                "Intake_Air_Temp_C": intake_temp,
                "Ambient_Temp_C": ambient,
                "Turbo_Boost_kPa": turbo_boost,
                "Exhaust_Gas_Temp_C": exhaust_temp,
                "Engine_Vibration_mm_s": vibration,
                "Brake_Pad_Wear_pct": brake_wear,
                "Tire_Pressure_psi": tire_pressure,
                "Transmission_Oil_Temp_C": trans_oil_temp,
                "Health_Index": health,
                "Degradation_Index": deg_idx,
                "RUL_hours": rul,
                "Timestamp_Hour": current_time.hour,
                "Timestamp_DayOfWeek": current_time.dayofweek,
                "Timestamp_Month": current_time.month
            }
            data.append(row)
            
    df = pd.DataFrame(data)
    
    thresh_val = df['Health_Index'].quantile(0.60) 
    df['RF_Abnormal_Label'] = (df['Health_Index'] < thresh_val).astype(int)
    
    df['Abnormal_Severity'] = 'No_Abnormality'
    df['Affected_Sensors'] = 'No_Abnormality'
    df['Abnormal_Pattern'] = 'No_Abnormality'
    df['Abnormal_Direction'] = 'No_Abnormality'
    df['Label_Source'] = 'Synthetic_Rule'
    
    df.loc[df['RF_Abnormal_Label'] == 1, 'Abnormal_Severity'] = 'High'
    df.loc[df['RF_Abnormal_Label'] == 1, 'Affected_Sensors'] = 'Multiple'
    df.loc[df['RF_Abnormal_Label'] == 1, 'Abnormal_Pattern'] = 'Degradation'
    df.loc[df['RF_Abnormal_Label'] == 1, 'Abnormal_Direction'] = 'High'
    
    # Enforce EXACT 16000 Normal and 24000 Abnormal
    # By quantile definition, it should be exactly 24000 ones since 40000 * 0.6 = 24000.
    
    csv_path = os.path.join(out_dir, "VEDA_Logistic_Officer_Corrected_RUL_Dataset.csv")
    df.to_csv(csv_path, index=False)
    
    meta = {
        "dataset_name": "VEDA Logistic Officer Corrected RUL Dataset V2",
        "generation_type": "fully_synthetic_from_scratch",
        "seed": 20260903,
        "fleet": {
            "total_vehicles": 40,
            "logistics_vehicles": 20,
            "officer_vehicles": 20
        },
        "records": {
            "total_rows": len(df),
            "rows_per_vehicle": obs_per_vehicle,
            "normal_rows": len(df[df['RF_Abnormal_Label'] == 0]),
            "abnormal_rows": len(df[df['RF_Abnormal_Label'] == 1])
        },
        "rul_definition": {
            "target": "RUL_hours",
            "basis": "Latent-Health-to-EOL"
        }
    }
    with open(os.path.join(out_dir, "VEDA_Logistic_Officer_Corrected_RUL_Dataset_Metadata.json"), "w") as f:
        json.dump(meta, f, indent=4)
        
    logistics = [f"LOV_{str(i+1).zfill(3)}" for i in range(20)]
    officers = [f"LOV_{str(i+21).zfill(3)}" for i in range(20)]
    np.random.shuffle(logistics)
    np.random.shuffle(officers)
    splits = {
        "train": logistics[:12] + officers[:12],
        "validation": logistics[12:16] + officers[12:16],
        "test": logistics[16:] + officers[16:]
    }
    with open(os.path.join(out_dir, "VEDA_Logistic_Officer_Corrected_RUL_Vehicle_Splits.json"), "w") as f:
        json.dump(splits, f, indent=4)
        
    print(f"V2 Dataset generated at {csv_path}")

if __name__ == "__main__":
    generate_dataset()
