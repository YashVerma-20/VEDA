import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')))

from agents.monitoring.schemas import MonitoringResult
from agents.diagnostics.schemas import DiagnosticsResult
from agents.prognostics.schemas import PrognosticsResult
from agents.maintenance_planning.schemas import MaintenancePlan
from agents.spare_parts.schemas import SparePartsRequirement
from agents.fleet_readiness.schemas import FleetReadinessInput, VehicleReadinessInput
from agents.fleet_readiness.agent import FleetReadinessAgent

@pytest.fixture
def agent():
    return FleetReadinessAgent()

def create_valid_vehicle(rul=350.0, severity="NORMAL", diag_prob="NONE", maint_rec="NO_IMMEDIATE_ACTION", m_status="SUCCESS"):
    m_res = MonitoringResult(
        vehicle_id="Tank_001", vehicle_class="TANK", timestamp=datetime.now(),
        abnormal_detected=(severity != "NORMAL"), severity=severity, status=m_status
    )
    d_res = DiagnosticsResult(
        vehicle_id="Tank_001", timestamp=datetime.now(), problem_detected=diag_prob,
        probable_cause="N/A", next_diagnostic_action="NONE", status="SUCCESS"
    )
    p_res = PrognosticsResult(
        vehicle_id="Tank_001", timestamp=datetime.now(), fusion_rul_hours=rul,
        degradation_trend="STABLE", risk_level="LOW", status="SUCCESS"
    )
    mp_res = MaintenancePlan(
        vehicle_id="Tank_001", timestamp=datetime.now(), maintenance_status="NOT_REQUIRED",
        recommended_action=maint_rec, priority="LOW", reason="N/A", estimated_duration_hours=0.0, status="SUCCESS"
    )
    sp_res = SparePartsRequirement(
        vehicle_id="Tank_001", timestamp=datetime.now(), parts_required=[],
        availability_status="NOT_AVAILABLE", status="SUCCESS",
        maintenance_reference="N/A", component="N/A", part_identifier="N/A",
        part_description="N/A", inventory_status="UNKNOWN", procurement_status="UNKNOWN",
        reason="N/A"
    )
    return VehicleReadinessInput(
        monitoring_result=m_res, diagnostics_result=d_res, prognostics_result=p_res,
        maintenance_plan=mp_res, spare_parts_requirement=sp_res
    )

def test_empty_fleet(agent):
    data = FleetReadinessInput(fleet_id="FLEET_1", vehicles={})
    res = agent.process(data)
    assert res.readiness_status == "UNKNOWN"

def test_ready_candidate(agent):
    data = FleetReadinessInput(fleet_id="F1", vehicles={"V1": create_valid_vehicle(rul=350.0)})
    res = agent.process(data)
    assert res.readiness_status == "READY"

def test_attention_rul(agent):
    data = FleetReadinessInput(fleet_id="F1", vehicles={"V1": create_valid_vehicle(rul=200.0)})
    res = agent.process(data)
    assert res.readiness_status == "ATTENTION"

def test_not_ready_rul(agent):
    data = FleetReadinessInput(fleet_id="F1", vehicles={"V1": create_valid_vehicle(rul=50.0)})
    res = agent.process(data)
    assert res.readiness_status == "NOT_READY"

def test_critical_diagnostic_blocks(agent):
    v = create_valid_vehicle(rul=400.0, severity="CRITICAL")
    data = FleetReadinessInput(fleet_id="F1", vehicles={"V1": v})
    res = agent.process(data)
    assert res.readiness_status == "NOT_READY"

def test_missing_data_is_unknown(agent):
    v = create_valid_vehicle(rul=400.0)
    v.prognostics_result = None
    data = FleetReadinessInput(fleet_id="F1", vehicles={"V1": v})
    res = agent.process(data)
    assert res.readiness_status == "UNKNOWN"

def test_maintenance_blocks(agent):
    v = create_valid_vehicle(rul=400.0, maint_rec="IMMEDIATE_REPAIR_REQUIRED")
    data = FleetReadinessInput(fleet_id="F1", vehicles={"V1": v})
    res = agent.process(data)
    assert res.readiness_status == "NOT_READY"

def test_fleet_attention_percentage(agent):
    vehicles = {
        "V1": create_valid_vehicle(rul=350.0),
        "V2": create_valid_vehicle(rul=350.0),
        "V3": create_valid_vehicle(rul=200.0),
        "V4": create_valid_vehicle(rul=350.0),
        "V5": create_valid_vehicle(rul=350.0)
    }
    data = FleetReadinessInput(fleet_id="F1", vehicles=vehicles)
    res = agent.process(data)
    assert res.readiness_status == "ATTENTION"

def test_fleet_not_ready_percentage(agent):
    vehicles = {
        "V1": create_valid_vehicle(rul=50.0),
        "V2": create_valid_vehicle(rul=50.0),
        "V3": create_valid_vehicle(rul=350.0),
        "V4": create_valid_vehicle(rul=350.0),
        "V5": create_valid_vehicle(rul=350.0)
    }
    data = FleetReadinessInput(fleet_id="F1", vehicles=vehicles)
    res = agent.process(data)
    assert res.readiness_status == "NOT_READY"

def test_fleet_not_ready_count(agent):
    vehicles = {
        "V1": create_valid_vehicle(rul=50.0),
        "V2": create_valid_vehicle(rul=50.0),
        "V3": create_valid_vehicle(rul=50.0),
    }
    for i in range(4, 21):
        vehicles[f"V{i}"] = create_valid_vehicle(rul=350.0)
    # 3/20 = 15%, but count >= 3 triggers NOT_READY
    data = FleetReadinessInput(fleet_id="F1", vehicles=vehicles)
    res = agent.process(data)
    assert res.readiness_status == "NOT_READY"

def test_unknown_propagation_overrides_ready(agent):
    # Rule: UNKNOWN overrides lower-severity states when required info is missing
    v = create_valid_vehicle(rul=350.0, m_status="INSUFFICIENT_DATA")
    data = FleetReadinessInput(fleet_id="F1", vehicles={"V1": v})
    res = agent.process(data)
    assert res.readiness_status == "UNKNOWN"
    
if __name__ == "__main__":
    pytest.main(["-v", __file__])
