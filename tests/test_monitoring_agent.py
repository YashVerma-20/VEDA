import pytest
from datetime import datetime
from pydantic import ValidationError
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')))

from agents.monitoring.schemas import MonitoringInput, MonitoringResult
from agents.monitoring.agent import MonitoringAgent

@pytest.fixture
def agent():
    return MonitoringAgent()

def test_normal_telemetry(agent):
    data = MonitoringInput(
        vehicle_id="Tank_001",
        vehicle_class="TANK",
        timestamp=datetime.now(),
        telemetry={"Engine_RPM": 1500},
        rf_abnormal_prediction=0,
        rf_abnormal_probability=0.1
    )
    result = agent.process(data)
    assert result.abnormal_detected is False
    assert result.severity == "NORMAL"
    assert result.status == "SUCCESS"

def test_abnormal_rf_result(agent):
    data = MonitoringInput(
        vehicle_id="Log_001",
        vehicle_class="LOGISTIC",
        timestamp=datetime.now(),
        telemetry={"Engine_RPM": 3500},
        rf_abnormal_prediction=1,
        rf_abnormal_probability=0.9
    )
    result = agent.process(data)
    assert result.abnormal_detected is True
    assert result.severity == "WARNING"
    assert "RF abnormality classification triggered." in result.observed_findings
    assert result.status == "SUCCESS"

def test_missing_telemetry(agent):
    data = MonitoringInput(
        vehicle_id="Tank_001",
        vehicle_class="TANK",
        timestamp=datetime.now(),
        telemetry={},  # Missing
        rf_abnormal_prediction=0
    )
    result = agent.process(data)
    assert result.status == "INSUFFICIENT_DATA"
    assert result.severity == "UNKNOWN"

def test_missing_rf_result(agent):
    data = MonitoringInput(
        vehicle_id="Tank_001",
        vehicle_class="TANK",
        timestamp=datetime.now(),
        telemetry={"Engine_RPM": 1500},
        rf_abnormal_prediction=None
    )
    result = agent.process(data)
    assert result.status == "UNAVAILABLE_RF"
    assert result.severity == "UNKNOWN"

def test_unknown_vehicle_type(agent):
    data = MonitoringInput(
        vehicle_id="UFO_001",
        vehicle_class="SPACESHIP",
        timestamp=datetime.now(),
        telemetry={"Speed": 9999},
        rf_abnormal_prediction=0
    )
    result = agent.process(data)
    assert result.status == "UNSUPPORTED_VEHICLE"
    assert result.severity == "UNKNOWN"

def test_no_fabricated_rul_fields():
    # Attempt to pass RUL to input should fail because extra='forbid'
    with pytest.raises(ValidationError):
        MonitoringInput(
            vehicle_id="Tank_001",
            vehicle_class="TANK",
            timestamp=datetime.now(),
            telemetry={"Engine_RPM": 1500},
            Actual_RUL=50.0  # Leakage prohibited
        )

def test_no_fabricated_confidence_in_result(agent):
    data = MonitoringInput(
        vehicle_id="Tank_001",
        vehicle_class="TANK",
        timestamp=datetime.now(),
        telemetry={"Engine_RPM": 1500},
        rf_abnormal_prediction=1,
        rf_abnormal_probability=0.88
    )
    result = agent.process(data)
    # The monitoring result should not contain an invented 'confidence' field.
    # It passes along rf_abnormal_probability in source_model_info, but does not invent a new confidence field.
    assert "rf_probability" in result.source_model_info
    assert result.source_model_info["rf_probability"] == 0.88
    
    with pytest.raises(AttributeError):
        _ = result.confidence

if __name__ == "__main__":
    pytest.main(["-v", __file__])
