import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import pandas as pd
import numpy as np
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "app")))
from main import app

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
    seq_df = seq_df.replace({np.nan: None})
    return str(vehicle_id), seq_df.to_dict('records')


def test_repeated_requests_consistency_and_caching():
    client = TestClient(app)
    vid, telemetry = get_tank_telemetry()
    payload = {
        "vehicle_id": vid,
        "vehicle_class": "TANK",
        "telemetry": telemetry
    }
    
    # Request 1 (should lazy-load models, takes longer)
    start_time = time.time()
    resp1 = client.post("/api/v1/inference/", json=payload)
    time1 = time.time() - start_time
    assert resp1.status_code == 200
    
    # Request 2 (should be cached, much faster)
    start_time = time.time()
    resp2 = client.post("/api/v1/inference/", json=payload)
    time2 = time.time() - start_time
    assert resp2.status_code == 200
    
    # Request 3
    start_time = time.time()
    resp3 = client.post("/api/v1/inference/", json=payload)
    time3 = time.time() - start_time
    assert resp3.status_code == 200
    
    # Verify deterministic consistency by checking static values
    def get_static_values(resp_dict):
        vid = list(resp_dict["vehicle_results"].keys())[0]
        v_res = resp_dict["vehicle_results"][vid]
        return {
            "rf_abnormal": v_res["monitoring"]["abnormal_detected"],
            "lstm_rul": v_res["prognostics"].get("lstm_rul_hours"),
            "xgb_rul": v_res["prognostics"].get("xgb_rul_hours"),
            "fusion_rul": v_res["prognostics"].get("fusion_rul_hours"),
            "fleet_status": resp_dict["fleet_status"]["readiness_status"]
        }
        
    assert get_static_values(resp1.json()) == get_static_values(resp2.json())
    assert get_static_values(resp2.json()) == get_static_values(resp3.json())
    
    # The models are large, so time1 > time2 significantly
    assert time1 > time2, f"Caching expected to make Req2 ({time2:.4f}s) faster than Req1 ({time1:.4f}s)"

@pytest.mark.asyncio
async def test_concurrent_vehicle_isolation():
    tank_vid, tank_telemetry = get_tank_telemetry()
    log_vid, log_telemetry = get_logistic_officer_telemetry(is_officer=False)
    off_vid, off_telemetry = get_logistic_officer_telemetry(is_officer=True)
    
    req_tank = {"vehicle_id": tank_vid, "vehicle_class": "TANK", "telemetry": tank_telemetry}
    req_log = {"vehicle_id": log_vid, "vehicle_class": "LOGISTIC TRUCK", "telemetry": log_telemetry}
    req_off = {"vehicle_id": off_vid, "vehicle_class": "OFFICER VEHICLE", "telemetry": off_telemetry}
    
    # We will send 6 requests concurrently: Tank, Logistic, Officer, Tank, Logistic, Officer
    payloads = [req_tank, req_log, req_off, req_tank, req_log, req_off]
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        tasks = [ac.post("/api/v1/inference/", json=p) for p in payloads]
        responses = await asyncio.gather(*tasks)
        
    for i, resp in enumerate(responses):
        assert resp.status_code == 200, f"Request {i} failed: {resp.text}"
        data = resp.json()
        expected_vid = payloads[i]["vehicle_id"]
        
        # Verify isolation: The response must match the expected vehicle ID
        assert expected_vid in data["vehicle_results"], f"Expected {expected_vid} but got {data['vehicle_results'].keys()}"
        
        prog = data["vehicle_results"][expected_vid]["prognostics"]
        lstm = prog.get("lstm_rul_hours")
        xgb = prog.get("xgb_rul_hours")
        fusion = prog.get("fusion_rul_hours")
        
        assert fusion is not None, "Fusion RUL should not be None"
        
        # Verify formula isolation based on class
        if payloads[i]["vehicle_class"] == "TANK":
            assert np.isclose(fusion, 1.00 * xgb)
        else:
            assert np.isclose(fusion, 0.30 * lstm + 0.70 * xgb)
