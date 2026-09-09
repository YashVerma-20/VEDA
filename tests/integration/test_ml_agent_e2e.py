import os
import json
import pytest
import pandas as pd
import numpy as np

# Adjust path for VEDA backend modules
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "app")))

from services.ml_inference_service import MLInferenceService
from agents.orchestration.orchestrator import VedaOrchestrator
from agents.orchestration.schemas import OrchestrationRequest, OrchestrationResult, VehicleOrchestrationRequest

def get_tank_telemetry():
    # Reconstruct raw telemetry from downstream xgb_test since raw is missing in snapshot
    test_meta = pd.read_csv(r"d:\VEDA\datasets\tank\downstream\test_metadata.csv")
    xgb_test = pd.read_csv(r"d:\VEDA\datasets\tank\downstream\xgb_test.csv")
    
    # Pick first vehicle
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
            ts_dict[col] = row_data[f"t{t:02d}__{col}"]
        timesteps.append(ts_dict)
        
    return vehicle_id, pd.DataFrame(timesteps)

def get_logistic_officer_telemetry(is_officer=False):
    df = pd.read_csv(r"d:\VEDA\datasets\logistic_officer\corrected_rul_v2\VEDA_Logistic_Officer_Corrected_RUL_Dataset.csv")
    target_class = 'Officer Vehicle' if is_officer else 'Logistic Truck'
    
    # Get the first vehicle of this class
    vehicle_df = df[df['Vehicle_Class'] == target_class]
    vehicle_id = vehicle_df['Vehicle_ID'].iloc[0]
    
    # Get first 30 rows for this vehicle
    seq_df = vehicle_df[vehicle_df['Vehicle_ID'] == vehicle_id].head(30).copy()
    
    # Exclude non-telemetry columns that the inference service doesn't expect (if any) or just leave it
    seq_df = seq_df.drop(columns=['Vehicle_ID', 'Vehicle_Class', 'RUL_Hours', 'Failure_Mode'], errors='ignore')
    
    return str(vehicle_id), seq_df

@pytest.fixture(scope="module")
def setup_services():
    ml_service = MLInferenceService()
    orchestrator = VedaOrchestrator()
    return ml_service, orchestrator

def validate_end_to_end(ml_service, orchestrator, vehicle_id, vehicle_class, df):
    # 1. ML Inference Service
    ml_req = ml_service.run_inference(vehicle_id, vehicle_class, df)
    
    # Validate mathematical fusion
    if vehicle_class.upper() == "TANK":
        if ml_req.fusion_rul_hours is not None:
            expected_fusion = 0.00 * ml_req.lstm_rul_hours + 1.00 * ml_req.xgb_rul_hours
            assert np.isclose(ml_req.fusion_rul_hours, expected_fusion), f"Fusion math failed for {vehicle_class}"
    else:
        if ml_req.fusion_rul_hours is not None:
            expected_fusion = 0.30 * ml_req.lstm_rul_hours + 0.70 * ml_req.xgb_rul_hours
            assert np.isclose(ml_req.fusion_rul_hours, expected_fusion), f"Fusion math failed for {vehicle_class}"
    
    # 2. Agent Orchestration
    req = OrchestrationRequest(
        request_id=f"TEST_{vehicle_id}",
        request_type="SINGLE_VEHICLE",
        fleet_id="TEST_FLEET",
        vehicles=[ml_req]
    )
    result = orchestrator.process(req)
    
    # Validate orchestration result
    assert isinstance(result, OrchestrationResult)
    assert result.status == "SUCCESS"
    
    v_res = result.vehicle_results[vehicle_id]
    
    # Validate Fleet Readiness Agent logic
    assert result.fleet_status is not None
    assert result.fleet_status.readiness_status in ["READY", "ATTENTION", "NOT_READY", "UNKNOWN"]
    
    # Validate Spare Parts Agent safe behavior
    sp_res = v_res["spare_parts"]
    assert sp_res is not None
    if ml_req.fusion_rul_hours is not None:
        # We don't have inventory, it should return safe unknown for parts
        assert sp_res["part_identifier"] in ["NOT_APPLICABLE", "PART_MAPPING_UNAVAILABLE", "UNKNOWN"]
        assert sp_res["inventory_status"] in ["NOT_APPLICABLE", "UNKNOWN"]
        assert sp_res["availability_status"] in ["NOT_APPLICABLE", "UNKNOWN", "UNKNOWN_OR_UNAVAILABLE"]

    return ml_req, result

def test_tank_e2e(setup_services):
    ml_service, orchestrator = setup_services
    vid, df = get_tank_telemetry()
    
    ml_req, result = validate_end_to_end(ml_service, orchestrator, vid, "TANK", df)
    
    print(f"\n[TANK] Vehicle ID: {vid}")
    print(f"RF Abnormal: {ml_req.rf_abnormal_class} ({ml_req.rf_abnormal_probability:.4f})")
    print(f"LSTM RUL: {ml_req.lstm_rul_hours:.2f} h")
    print(f"XGB RUL: {ml_req.xgb_rul_hours:.2f} h")
    print(f"Fusion RUL: {ml_req.fusion_rul_hours:.2f} h")
    print(f"Fleet Readiness: {result.fleet_status.readiness_status}")

def test_logistic_e2e(setup_services):
    ml_service, orchestrator = setup_services
    vid, df = get_logistic_officer_telemetry(is_officer=False)
    
    ml_req, result = validate_end_to_end(ml_service, orchestrator, vid, "LOGISTIC", df)
    
    print(f"\n[LOGISTIC] Vehicle ID: {vid}")
    print(f"RF Abnormal: {ml_req.rf_abnormal_class} ({ml_req.rf_abnormal_probability:.4f})")
    print(f"LSTM RUL: {ml_req.lstm_rul_hours:.2f} h")
    print(f"XGB RUL: {ml_req.xgb_rul_hours:.2f} h")
    print(f"Fusion RUL: {ml_req.fusion_rul_hours:.2f} h")
    print(f"Fleet Readiness: {result.fleet_status.readiness_status}")

def test_officer_e2e(setup_services):
    ml_service, orchestrator = setup_services
    vid, df = get_logistic_officer_telemetry(is_officer=True)
    
    ml_req, result = validate_end_to_end(ml_service, orchestrator, vid, "OFFICER", df)
    
    print(f"\n[OFFICER] Vehicle ID: {vid}")
    print(f"RF Abnormal: {ml_req.rf_abnormal_class} ({ml_req.rf_abnormal_probability:.4f})")
    print(f"LSTM RUL: {ml_req.lstm_rul_hours:.2f} h")
    print(f"XGB RUL: {ml_req.xgb_rul_hours:.2f} h")
    print(f"Fusion RUL: {ml_req.fusion_rul_hours:.2f} h")
    print(f"Fleet Readiness: {result.fleet_status.readiness_status}")

def test_insufficient_data_e2e(setup_services):
    ml_service, orchestrator = setup_services
    vid, df = get_tank_telemetry()
    
    # Truncate to less than 30 rows
    short_df = df.head(15).copy()
    
    ml_req = ml_service.run_inference(vid, "TANK", short_df)
    
    assert ml_req.rf_abnormal_class is not None
    assert ml_req.lstm_rul_hours is None
    assert ml_req.xgb_rul_hours is None
    assert ml_req.fusion_rul_hours is None
    
    req = OrchestrationRequest(
        request_id=f"TEST_SHORT_{vid}",
        request_type="SINGLE_VEHICLE",
        fleet_id="TEST_FLEET",
        vehicles=[ml_req]
    )
    result = orchestrator.process(req)
    
    assert result.fleet_status.readiness_status in ["UNKNOWN", "NOT_READY"]

if __name__ == "__main__":
    # Execute manually to see printed trace
    ml, orch = setup_services()
    print("Executing tests manually for trace...")
    test_tank_e2e((ml, orch))
    test_logistic_e2e((ml, orch))
    test_officer_e2e((ml, orch))
    test_insufficient_data_e2e((ml, orch))
