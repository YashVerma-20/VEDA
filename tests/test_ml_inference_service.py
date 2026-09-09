import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app")))

import pytest
import numpy as np
import pandas as pd
from services.ml_inference_service import MLInferenceService
from agents.orchestration.schemas import VehicleOrchestrationRequest

@pytest.fixture(scope="module")
def ml_service():
    return MLInferenceService()

def test_tank_real_inference_success(ml_service):
    # Dummy raw telemetry (18 columns + 1 ID + 1 timestamp etc.)
    # We'll need at least 30 rows. Actually 39 rows to compute past mean correctly for all 30!
    # Wait, the rolling(10) uses min_periods=1, so it won't be NaN, but let's provide 30 rows.
    np.random.seed(42)
    data = {
        "Operating_Hours": np.linspace(100, 110, 30),
        "Odometer_km": np.linspace(1000, 1050, 30),
        "Engine_RPM": np.random.uniform(1000, 2000, 30),
        "Speed_kmph": np.random.uniform(10, 50, 30),
        "Coolant_Temp_C": np.random.uniform(80, 100, 30),
        "Oil_Temp_C": np.random.uniform(90, 110, 30),
        "Oil_Pressure_bar": np.random.uniform(2, 5, 30),
        "Fuel_Level_pct": np.random.uniform(20, 80, 30),
        "Battery_Voltage_V": np.random.uniform(22, 28, 30),
        "Engine_Load_pct": np.random.uniform(10, 90, 30),
        "Throttle_Position_pct": np.random.uniform(10, 90, 30),
        "Intake_Air_Temp_C": np.random.uniform(20, 40, 30),
        "Ambient_Temp_C": np.random.uniform(15, 35, 30),
        "Turbo_Boost_kPa": np.random.uniform(100, 200, 30),
        "Exhaust_Gas_Temp_C": np.random.uniform(300, 600, 30),
        "Engine_Vibration_mm_s": np.random.uniform(1, 10, 30),
        "Brake_Pad_Wear_pct": np.random.uniform(10, 50, 30),
        "Tire_Pressure_psi": np.random.uniform(30, 40, 30),
    }
    df = pd.DataFrame(data)
    
    result = ml_service.run_inference("TANK_001", "TANK", df)
    
    assert isinstance(result, VehicleOrchestrationRequest)
    assert result.vehicle_id == "TANK_001"
    assert result.rf_abnormal_class in ["normal", "abnormal"]
    assert result.lstm_rul_hours is not None
    assert result.xgb_rul_hours is not None
    assert result.fusion_rul_hours is not None
    
    # Check that fusion RUL == XGB RUL since weight is 0.00 / 1.00
    assert np.isclose(result.fusion_rul_hours, result.xgb_rul_hours)

def test_logistic_real_inference_success(ml_service):
    np.random.seed(42)
    data = {
        "Operating_Terrain": ["Desert"] * 30,
        "Odometer_km": np.linspace(1000, 1050, 30),
        "Engine_RPM": np.random.uniform(1000, 2000, 30),
        "Speed_kmph": np.random.uniform(10, 50, 30),
        "Coolant_Temp_C": np.random.uniform(80, 100, 30),
        "Oil_Temp_C": np.random.uniform(90, 110, 30),
        "Oil_Pressure_bar": np.random.uniform(2, 5, 30),
        "Fuel_Level_pct": np.random.uniform(20, 80, 30),
        "Battery_Voltage_V": np.random.uniform(22, 28, 30),
        "Engine_Load_pct": np.random.uniform(10, 90, 30),
        "Throttle_Position_pct": np.random.uniform(10, 90, 30),
        "Intake_Air_Temp_C": np.random.uniform(20, 40, 30),
        "Ambient_Temp_C": np.random.uniform(15, 35, 30),
        "Turbo_Boost_kPa": np.random.uniform(100, 200, 30),
        "Exhaust_Gas_Temp_C": np.random.uniform(300, 600, 30),
        "Engine_Vibration_mm_s": np.random.uniform(1, 10, 30),
        "Brake_Pad_Wear_pct": np.random.uniform(10, 50, 30),
        "Tire_Pressure_psi": np.random.uniform(30, 40, 30),
        "Transmission_Oil_Temp_C": np.random.uniform(70, 90, 30),
        "Timestamp_Hour": np.random.randint(0, 24, 30),
        "Timestamp_DayOfWeek": np.random.randint(0, 7, 30),
        "Timestamp_Month": np.random.randint(1, 13, 30),
    }
    df = pd.DataFrame(data)
    
    result = ml_service.run_inference("LOG_001", "LOGISTIC", df)
    
    assert isinstance(result, VehicleOrchestrationRequest)
    assert result.vehicle_id == "LOG_001"
    assert result.rf_abnormal_class in ["normal", "abnormal"]
    assert result.lstm_rul_hours is not None
    assert result.xgb_rul_hours is not None
    assert result.fusion_rul_hours is not None
    
    expected_fusion = 0.30 * result.lstm_rul_hours + 0.70 * result.xgb_rul_hours
    assert np.isclose(result.fusion_rul_hours, expected_fusion)

def test_insufficient_data(ml_service):
    data = {
        "Operating_Terrain": ["Desert"] * 5,
        "Odometer_km": np.linspace(1000, 1010, 5),
        "Engine_RPM": np.random.uniform(1000, 2000, 5),
        "Speed_kmph": np.random.uniform(10, 50, 5),
        "Coolant_Temp_C": np.random.uniform(80, 100, 5),
        "Oil_Temp_C": np.random.uniform(90, 110, 5),
        "Oil_Pressure_bar": np.random.uniform(2, 5, 5),
        "Fuel_Level_pct": np.random.uniform(20, 80, 5),
        "Battery_Voltage_V": np.random.uniform(22, 28, 5),
        "Engine_Load_pct": np.random.uniform(10, 90, 5),
        "Throttle_Position_pct": np.random.uniform(10, 90, 5),
        "Intake_Air_Temp_C": np.random.uniform(20, 40, 5),
        "Ambient_Temp_C": np.random.uniform(15, 35, 5),
        "Turbo_Boost_kPa": np.random.uniform(100, 200, 5),
        "Exhaust_Gas_Temp_C": np.random.uniform(300, 600, 5),
        "Engine_Vibration_mm_s": np.random.uniform(1, 10, 5),
        "Brake_Pad_Wear_pct": np.random.uniform(10, 50, 5),
        "Tire_Pressure_psi": np.random.uniform(30, 40, 5),
        "Transmission_Oil_Temp_C": np.random.uniform(70, 90, 5),
        "Timestamp_Hour": np.random.randint(0, 24, 5),
        "Timestamp_DayOfWeek": np.random.randint(0, 7, 5),
        "Timestamp_Month": np.random.randint(1, 13, 5),
    }
    df = pd.DataFrame(data)
    
    result = ml_service.run_inference("LOG_002", "LOGISTIC", df)
    
    assert result.rf_abnormal_class is not None  # RF works on single/few rows
    assert result.lstm_rul_hours is None  # RULs should be None because we have <30 rows
    assert result.xgb_rul_hours is None
    assert result.fusion_rul_hours is None

def test_missing_features(ml_service):
    data = {
        "Odometer_km": np.linspace(1000, 1010, 30),
    }
    df = pd.DataFrame(data)
    
    with pytest.raises(ValueError, match="Missing RF features"):
        ml_service.run_inference("LOG_003", "LOGISTIC", df)
