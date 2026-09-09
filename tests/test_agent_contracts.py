import pytest
from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import Optional, List
from datetime import datetime

# ==========================================
# CONTRACT SCHEMAS
# ==========================================

class ModelAgentInput(BaseModel):
    vehicle_id: str
    vehicle_class: str
    timestamp: datetime
    rf_abnormal_probability: Optional[float] = None
    rf_abnormal_prediction: Optional[int] = None
    lstm_rul_prediction: Optional[float] = None
    xgboost_rul_prediction: Optional[float] = None
    fusion_rul_prediction: Optional[float] = None

    @model_validator(mode='after')
    def prohibit_training_fields(self):
        # We simulate the prohibition by checking if forbidden fields accidentally got passed in kwargs
        # Pydantic v2 handles this by default with extra='forbid', but let's explicitly reject them if we used extra='allow'
        pass
        
    model_config = {
        "extra": "forbid"  # Strictly forbids 'Actual_RUL', 'Health_Index', etc.
    }

class MonitoringResult(BaseModel):
    vehicle_id: str
    vehicle_class: str
    timestamp: datetime
    abnormal_detected: bool
    severity: str

class DiagnosticsResult(BaseModel):
    vehicle_id: str
    timestamp: datetime
    problem_detected: str
    evidence_sensors: List[str]
    probable_cause: str
    confidence: Optional[float] = None  # Optional, must not be invented if unavailable
    next_diagnostic_action: str

class PrognosticsResult(BaseModel):
    vehicle_id: str
    timestamp: datetime
    fusion_rul_hours: Optional[float] = None
    degradation_trend: str
    risk_level: str

# ==========================================
# TESTS
# ==========================================

def test_model_input_prohibits_ground_truth():
    # Providing 'Actual_RUL' should fail due to extra='forbid'
    with pytest.raises(ValidationError):
        ModelAgentInput(
            vehicle_id="Tank_001",
            vehicle_class="TANK",
            timestamp=datetime.now(),
            fusion_rul_prediction=45.2,
            Actual_RUL=40.0  # PROHIBITED
        )

def test_model_input_prohibits_future_info():
    with pytest.raises(ValidationError):
        ModelAgentInput(
            vehicle_id="Log_001",
            vehicle_class="LOGISTIC",
            timestamp=datetime.now(),
            Health_Index=0.5  # PROHIBITED
        )

def test_valid_model_input():
    # Should pass without forbidden fields
    valid_input = ModelAgentInput(
        vehicle_id="Log_001",
        vehicle_class="LOGISTIC",
        timestamp=datetime.now(),
        rf_abnormal_probability=0.85,
        rf_abnormal_prediction=1,
        fusion_rul_prediction=32.5
    )
    assert valid_input.vehicle_id == "Log_001"
    assert valid_input.fusion_rul_prediction == 32.5

def test_diagnostics_confidence_optional():
    # Confidence is optional, ensuring agents don't have to fabricate it
    diag = DiagnosticsResult(
        vehicle_id="Tank_001",
        timestamp=datetime.now(),
        problem_detected="Engine Overheating",
        evidence_sensors=["Coolant_Temp"],
        probable_cause="Coolant Leak",
        next_diagnostic_action="Inspect Radiator"
    )
    assert diag.confidence is None

def test_prognostics_handles_missing_rul():
    # If ML output is unavailable, fusion_rul_hours should be None (explicitly handled)
    prog = PrognosticsResult(
        vehicle_id="Off_001",
        timestamp=datetime.now(),
        fusion_rul_hours=None,
        degradation_trend="Unknown",
        risk_level="HIGH"  # Risk can be high based on diagnostics even if RUL is missing
    )
    assert prog.fusion_rul_hours is None

if __name__ == "__main__":
    pytest.main(["-v", __file__])
