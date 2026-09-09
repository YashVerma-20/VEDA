import pytest
from datetime import datetime
import math
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')))

from agents.monitoring.schemas import MonitoringResult
from agents.diagnostics.schemas import DiagnosticsResult
from agents.prognostics.schemas import PrognosticsInput, PrognosticsResult
from agents.prognostics.agent import PrognosticsAgent

@pytest.fixture
def agent():
    return PrognosticsAgent()

def create_mr(status="SUCCESS"):
    return MonitoringResult(
        vehicle_id="Tank_001",
        vehicle_class="TANK",
        timestamp=datetime.now(),
        abnormal_detected=False,
        severity="NORMAL",
        observed_findings=[],
        source_model_info={},
        status=status,
        execution_metadata={}
    )

def test_valid_fusion_rul(agent):
    mr = create_mr()
    data = PrognosticsInput(
        monitoring_result=mr,
        diagnostics_result=None,
        lstm_rul_hours=45.0,
        xgb_rul_hours=55.0,
        fusion_rul_hours=52.0  # 0.3 * 45 + 0.7 * 55
    )
    res = agent.process(data)
    
    assert res.status == "AVAILABLE"
    assert res.fusion_rul_hours == 52.0
    assert res.lstm_rul_hours == 45.0
    assert res.xgb_rul_hours == 55.0
    assert res.risk_level == "NORMAL"

def test_missing_fusion_rul_no_recalculation(agent):
    mr = create_mr()
    data = PrognosticsInput(
        monitoring_result=mr,
        diagnostics_result=None,
        lstm_rul_hours=45.0,
        xgb_rul_hours=55.0,
        fusion_rul_hours=None
    )
    res = agent.process(data)
    
    assert res.status == "PARTIAL_MODELS_AVAILABLE"
    assert res.fusion_rul_hours is None  # MUST NOT BE RECALCULATED

def test_invalid_rul_nan_infinity_negative(agent):
    mr = create_mr()
    data = PrognosticsInput(
        monitoring_result=mr,
        fusion_rul_hours=float('nan'),
        lstm_rul_hours=float('inf'),
        xgb_rul_hours=-10.0
    )
    res = agent.process(data)
    
    assert res.status == "UNAVAILABLE"
    assert res.fusion_rul_hours is None
    assert res.lstm_rul_hours is None
    assert res.xgb_rul_hours is None

def test_unsupported_vehicle_propages(agent):
    mr = create_mr(status="UNSUPPORTED_VEHICLE")
    data = PrognosticsInput(
        monitoring_result=mr,
        fusion_rul_hours=40.0
    )
    res = agent.process(data)
    
    assert res.status == "INVALID"
    assert res.fusion_rul_hours == 40.0  # Passed through but marked invalid

def test_diagnostics_conflict(agent):
    mr = create_mr()
    dr = DiagnosticsResult(
        vehicle_id="Tank_001",
        timestamp=datetime.now(),
        problem_detected="CONFLICT",
        evidence_sensors=[],
        probable_cause="",
        next_diagnostic_action="HUMAN_REVIEW",
        status="CONFLICT"
    )
    data = PrognosticsInput(
        monitoring_result=mr,
        diagnostics_result=dr,
        fusion_rul_hours=40.0
    )
    res = agent.process(data)
    
    assert res.status == "CONFLICT"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
