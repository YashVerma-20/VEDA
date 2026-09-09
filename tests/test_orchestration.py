import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')))

from agents.orchestration.schemas import OrchestrationRequest, VehicleOrchestrationRequest
from agents.orchestration.orchestrator import VedaOrchestrator

@pytest.fixture
def orchestrator():
    return VedaOrchestrator()

def test_single_vehicle_orchestration(orchestrator):
    v_req = VehicleOrchestrationRequest(
        vehicle_id="Tank_001",
        vehicle_class="TANK",
        telemetry={"temperature": 85.0},
        rf_abnormal_class=None,
        fusion_rul_hours=120.0
    )
    req = OrchestrationRequest(
        request_id="REQ_001",
        request_type="SINGLE_VEHICLE",
        vehicles=[v_req]
    )
    
    res = orchestrator.process(req)
    
    assert res.status == "SUCCESS"
    assert "Tank_001" in res.vehicle_results
    assert res.fleet_status is not None
    
    trace = res.execution_trace
    assert len(trace) == 2 # 1 vehicle + 1 fleet
    
    v_trace = trace[0]["steps"]
    agents_run = [step["agent"] for step in v_trace]
    assert "MonitoringAgent" in agents_run
    assert "DiagnosticsAgent" in agents_run
    assert "PrognosticsAgent" in agents_run
    assert "MaintenancePlanningAgent" in agents_run
    assert "SparePartsAgent" in agents_run

def test_multi_vehicle_orchestration(orchestrator):
    v_req1 = VehicleOrchestrationRequest(
        vehicle_id="Tank_001",
        vehicle_class="TANK",
        telemetry={"temperature": 85.0}
    )
    v_req2 = VehicleOrchestrationRequest(
        vehicle_id="LO_002",
        vehicle_class="LOGISTIC_OFFICER",
        telemetry={"pressure": 120.0},
        fusion_rul_hours=45.0
    )
    req = OrchestrationRequest(
        request_id="REQ_002",
        request_type="FLEET",
        fleet_id="MIXED_FLEET",
        vehicles=[v_req1, v_req2]
    )
    
    res = orchestrator.process(req)
    
    assert res.status == "SUCCESS"
    assert "Tank_001" in res.vehicle_results
    assert "LO_002" in res.vehicle_results
    
    # Fleet agent should process both
    assert res.fleet_status.fleet_id == "MIXED_FLEET"
    assert "Tank_001" in res.fleet_status.vehicle_summaries
    assert "LO_002" in res.fleet_status.vehicle_summaries

def test_unsupported_vehicle_propagates_correctly(orchestrator):
    v_req = VehicleOrchestrationRequest(
        vehicle_id="UFO_999",
        vehicle_class="UNKNOWN_CLASS"
    )
    req = OrchestrationRequest(
        request_id="REQ_003",
        request_type="SINGLE_VEHICLE",
        vehicles=[v_req]
    )
    
    res = orchestrator.process(req)
    
    assert res.status == "SUCCESS"
    v_res = res.vehicle_results["UFO_999"]
    assert v_res["monitoring"]["status"] == "UNSUPPORTED_VEHICLE"
    assert v_res["diagnostics"]["status"] == "INSUFFICIENT_EVIDENCE"
    assert v_res["prognostics"]["status"] == "INVALID"
    
if __name__ == "__main__":
    pytest.main(["-v", __file__])
