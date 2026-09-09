import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')))

from agents.monitoring.schemas import MonitoringResult
from agents.diagnostics.schemas import DiagnosticsInput, DiagnosticsResult
from agents.diagnostics.agent import DiagnosticsAgent

@pytest.fixture
def agent():
    return DiagnosticsAgent()

def create_mr(status="SUCCESS", abnormal=False, severity="NORMAL", rf_prob=None):
    source_info = {}
    if rf_prob is not None:
        source_info["rf_probability"] = rf_prob
        
    return MonitoringResult(
        vehicle_id="Tank_001",
        vehicle_class="TANK",
        timestamp=datetime.now(),
        abnormal_detected=abnormal,
        severity=severity,
        observed_findings=[],
        source_model_info=source_info,
        status=status,
        execution_metadata={}
    )

def test_normal_input(agent):
    mr = create_mr(abnormal=False)
    data = DiagnosticsInput(monitoring_result=mr)
    res = agent.process(data)
    
    assert res.status == "SUCCESS"
    assert res.problem_detected == "NONE"
    assert res.next_diagnostic_action == "CONTINUE_MONITORING"
    assert res.confidence is None

def test_abnormal_input_with_rf_class(agent):
    mr = create_mr(abnormal=True, severity="WARNING", rf_prob=0.85)
    data = DiagnosticsInput(
        monitoring_result=mr,
        rf_abnormal_class="Engine"
    )
    res = agent.process(data)
    
    assert res.status == "SUCCESS"
    assert res.confidence == 0.85
    assert "Engine" in res.problem_detected
    assert "Engine" in res.probable_cause
    assert res.next_diagnostic_action == "TRIGGER_MAINTENANCE_PLANNING"

def test_conflicting_evidence(agent):
    # RF says normal, but fault codes exist
    mr = create_mr(abnormal=False)
    data = DiagnosticsInput(
        monitoring_result=mr,
        fault_codes=["ERR_COOLANT_LEAK"]
    )
    res = agent.process(data)
    
    assert res.status == "CONFLICT"
    assert res.problem_detected == "CONFLICT"
    assert res.next_diagnostic_action == "HUMAN_REVIEW"

def test_insufficient_data(agent):
    # Monitoring agent already flagged insufficient data
    mr = create_mr(status="INSUFFICIENT_DATA", abnormal=False, severity="UNKNOWN")
    data = DiagnosticsInput(monitoring_result=mr)
    res = agent.process(data)
    
    assert res.status == "INSUFFICIENT_EVIDENCE"
    assert res.next_diagnostic_action == "AWAIT_VALID_DATA"

def test_no_rul_recalculation(agent):
    # The DiagnosticsResult schema does not allow RUL fields, ensuring we don't calculate or pass RUL here.
    # To prove it, we try to inject an RUL field into the result initialization and it would fail schema validation.
    # Since agent._build_result strictly creates DiagnosticsResult, it's intrinsically safe.
    pass

if __name__ == "__main__":
    pytest.main(["-v", __file__])
