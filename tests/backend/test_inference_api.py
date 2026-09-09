import pytest
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "app")))
from main import app

client = TestClient(app)

def get_tank_telemetry():
    test_meta = pd.read_csv(r"d:\VEDA\datasets\tank\downstream\test_metadata.csv")
    xgb_test = pd.read_csv(r"d:\VEDA\datasets\tank\downstream\xgb_test.csv")
    first_row_idx = 0
    vehicle_id = str(test_meta.iloc[first_row_idx]['Vehicle_ID'])
    row_data = xgb_test.iloc[first_row_idx]
    
    raw_cols = [
        "Operating_Hours", "Odometer_km", "Engine_RPM", "Speed_kmph", 
        "Coolant_Temp_C", "Oil_Temp_C", "Oil_Pressure_bar", "Fuel_Level_pct", 
        "Battery_Voltage_V", "Engine_Load_pct", "Throttle_Position_pct", 
        "Intake_Air_Temp_C", "Ambient_Temp_C", "Turbo_Boost_kPa", 
        "Exhaust_Gas_Temp_C", "Engine_Vibration_mm_s", "Brake_Pad_Wear_pct", 
        "Tire_Pressure_psi"
    ]
    timesteps = []
    for t in range(30):
        ts_dict = {}
        for col in raw_cols:
            ts_dict[col] = float(row_data[f"t{t:02d}__{col}"])
        timesteps.append(ts_dict)
    return vehicle_id, timesteps

def get_logistic_officer_telemetry(is_officer=False):
    df = pd.read_csv(r"d:\VEDA\datasets\logistic_officer\corrected_rul_v2\VEDA_Logistic_Officer_Corrected_RUL_Dataset.csv")
    target_class = 'Officer Vehicle' if is_officer else 'Logistic Truck'
    vehicle_df = df[df['Vehicle_Class'] == target_class]
    vehicle_id = vehicle_df['Vehicle_ID'].iloc[0]
    seq_df = vehicle_df[vehicle_df['Vehicle_ID'] == vehicle_id].head(30).copy()
    seq_df = seq_df.drop(columns=['Vehicle_ID', 'Vehicle_Class', 'RUL_Hours', 'Failure_Mode'], errors='ignore')
    # replace NaN with None for JSON
    seq_df = seq_df.replace({np.nan: None})
    return str(vehicle_id), seq_df.to_dict('records')

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_inference_api_tank():
    vid, telemetry = get_tank_telemetry()
    payload = {
        "vehicle_id": vid,
        "vehicle_class": "TANK",
        "telemetry": telemetry
    }
    response = client.post("/api/v1/inference/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    v_res = data["vehicle_results"][vid]
    
    # Check fusion math
    prog = v_res["prognostics"]
    lstm = prog.get("lstm_rul_hours")
    xgb = prog.get("xgb_rul_hours")
    fusion = prog.get("fusion_rul_hours")
    
    assert lstm is not None
    assert xgb is not None
    assert fusion is not None
    expected = 0.00 * lstm + 1.00 * xgb
    assert np.isclose(fusion, expected)
    
    assert data["fleet_status"]["readiness_status"] in ["READY", "ATTENTION", "NOT_READY"]

def test_inference_api_logistic():
    vid, telemetry = get_logistic_officer_telemetry(is_officer=False)
    payload = {
        "vehicle_id": vid,
        "vehicle_class": "LOGISTIC TRUCK",
        "telemetry": telemetry
    }
    response = client.post("/api/v1/inference/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    v_res = data["vehicle_results"][vid]
    
    prog = v_res["prognostics"]
    lstm = prog.get("lstm_rul_hours")
    xgb = prog.get("xgb_rul_hours")
    fusion = prog.get("fusion_rul_hours")
    
    assert lstm is not None
    assert xgb is not None
    assert fusion is not None
    expected = 0.30 * lstm + 0.70 * xgb
    assert np.isclose(fusion, expected)

def test_inference_api_officer():
    vid, telemetry = get_logistic_officer_telemetry(is_officer=True)
    payload = {
        "vehicle_id": vid,
        "vehicle_class": "OFFICER VEHICLE",
        "telemetry": telemetry
    }
    response = client.post("/api/v1/inference/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    v_res = data["vehicle_results"][vid]
    
    prog = v_res["prognostics"]
    lstm = prog.get("lstm_rul_hours")
    xgb = prog.get("xgb_rul_hours")
    fusion = prog.get("fusion_rul_hours")
    
    assert lstm is not None
    assert xgb is not None
    assert fusion is not None
    expected = 0.30 * lstm + 0.70 * xgb
    assert np.isclose(fusion, expected)

def test_inference_api_insufficient_data():
    vid, telemetry = get_tank_telemetry()
    short_telemetry = telemetry[:15]
    payload = {
        "vehicle_id": vid,
        "vehicle_class": "TANK",
        "telemetry": short_telemetry
    }
    response = client.post("/api/v1/inference/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    v_res = data["vehicle_results"][vid]
    
    prog = v_res["prognostics"]
    assert prog.get("lstm_rul_hours") is None
    assert prog.get("xgb_rul_hours") is None
    assert prog.get("fusion_rul_hours") is None
    
    assert data["fleet_status"]["readiness_status"] in ["UNKNOWN", "NOT_READY"]

def test_inference_api_invalid_class():
    vid, telemetry = get_tank_telemetry()
    payload = {
        "vehicle_id": vid,
        "vehicle_class": "INVALID_CLASS",
        "telemetry": telemetry
    }
    response = client.post("/api/v1/inference/", json=payload)
    assert response.status_code == 400
    assert "Invalid vehicle_class" in response.json()["detail"]

def test_inference_api_missing_field():
    vid, telemetry = get_tank_telemetry()
    payload = {
        "vehicle_class": "TANK",
        "telemetry": telemetry
    } # Missing vehicle_id
    response = client.post("/api/v1/inference/", json=payload)
    assert response.status_code == 422 # Pydantic validation error
