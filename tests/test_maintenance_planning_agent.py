import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')))

from agents.monitoring.schemas import MonitoringResult
from agents.diagnostics.schemas import DiagnosticsResult
from agents.prognostics.schemas import PrognosticsResult
from agents.maintenance_planning.schemas import MaintenancePlanningInput, MaintenancePlan
from agents.maintenance_planning.agent import MaintenancePlanningAgent

@pytest.fixture
def agent():
    return MaintenancePlanningAgent()

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

def create_dr(status="SUCCESS", problem="NONE", cause="System operating normally."):
    return DiagnosticsResult(
        vehicle_id="Tank_001",
        timestamp=datetime.now(),
        problem_detected=problem,
        evidence_sensors=[],
        probable_cause=cause,
        confidence=None,
        next_diagnostic_action="CONTINUE_MONITORING",
        status=status,
        execution_metadata={}
    )

def create_pr(status="AVAILABLE", trend="STABLE", fusion=None):
    return PrognosticsResult(
        vehicle_id="Tank_001",
        timestamp=datetime.now(),
        fusion_rul_hours=fusion,
        lstm_rul_hours=None,
        xgb_rul_hours=None,
        degradation_trend=trend,
        risk_level="NORMAL",
        status=status,
        execution_metadata={}
    )

def test_normal_input(agent):
    data = MaintenancePlanningInput(
        monitoring_result=create_mr(),
        diagnostics_result=create_dr(),
        prognostics_result=create_pr()
    )
    res = agent.process(data)
    
    assert res.status == "SUCCESS"
    assert res.maintenance_status == "UNKNOWN"
    assert "No action required" in res.recommended_action
    assert res.estimated_time_frame_hours is None

def test_abnormal_diagnostic_input(agent):
    dr = create_dr(problem="Engine Overheat", cause="Coolant Leak")
    pr = create_pr(fusion=40.0)
    data = MaintenancePlanningInput(
        monitoring_result=create_mr(),
        diagnostics_result=dr,
        prognostics_result=pr
    )
    res = agent.process(data)
    
    assert res.status == "SUCCESS"
    assert res.maintenance_status == "RECOMMENDED"
    assert "RECOMMENDED: Inspect and service Coolant Leak" in res.recommended_action
    assert "40.0" in res.reason
    assert "Requires approved policy information" in res.constraints_missing_info[0]

def test_conflict_upstream(agent):
    dr = create_dr(status="CONFLICT")
    data = MaintenancePlanningInput(
        monitoring_result=create_mr(),
        diagnostics_result=dr,
        prognostics_result=create_pr()
    )
    res = agent.process(data)
    
    assert res.status == "CONFLICT"
    assert res.maintenance_status == "UNKNOWN"

def test_no_fabricated_completion(agent):
    # The agent explicitly prevents returning "COMPLETED" status.
    dr = create_dr(problem="Engine Overheat", cause="Coolant Leak")
    data = MaintenancePlanningInput(
        monitoring_result=create_mr(),
        diagnostics_result=dr,
        prognostics_result=create_pr()
    )
    res = agent.process(data)
    assert res.maintenance_status != "COMPLETED"
    assert res.maintenance_status == "RECOMMENDED"
    assert res.estimated_time_frame_hours is None # No fabricated duration

if __name__ == "__main__":
    pytest.main(["-v", __file__])
