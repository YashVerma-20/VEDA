import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')))

from agents.maintenance_planning.schemas import MaintenancePlan
from agents.spare_parts.schemas import SparePartsInput, SparePartsRequirement
from agents.spare_parts.agent import SparePartsAgent

@pytest.fixture
def agent():
    return SparePartsAgent()

def create_mp(status="SUCCESS", m_status="RECOMMENDED", action="Inspect and service Coolant Leak"):
    return MaintenancePlan(
        vehicle_id="Tank_001",
        timestamp=datetime.now(),
        recommended_action=action,
        priority="UNKNOWN",
        reason="Test reason",
        estimated_time_frame_hours=None,
        maintenance_status=m_status,
        constraints_missing_info=[],
        status=status,
        execution_metadata={}
    )

def test_no_maintenance_recommended(agent):
    mp = create_mp(m_status="UNKNOWN", action="No action required")
    data = SparePartsInput(maintenance_plan=mp)
    res = agent.process(data)
    
    assert res.inventory_status == "NOT_APPLICABLE"
    assert res.quantity is None
    assert res.part_identifier == "NOT_APPLICABLE"

def test_maintenance_recommended_but_no_inventory_source(agent):
    mp = create_mp()
    data = SparePartsInput(maintenance_plan=mp)
    res = agent.process(data)
    
    # Crucially, since there's no inventory source, it MUST be UNKNOWN
    assert res.inventory_status == "UNKNOWN"
    assert res.procurement_status == "UNKNOWN"
    assert res.availability_status == "UNKNOWN"
    assert res.quantity is None
    assert res.part_identifier == "PART_MAPPING_UNAVAILABLE"
    assert res.source_information["inventory_source_available"] is False
    assert res.source_information["part_mapping_available"] is False

def test_upstream_conflict(agent):
    mp = create_mp(status="CONFLICT")
    data = SparePartsInput(maintenance_plan=mp)
    res = agent.process(data)
    
    assert res.inventory_status == "UNKNOWN"
    assert res.part_identifier == "UNKNOWN"
    assert "conflict" in res.reason.lower()

if __name__ == "__main__":
    pytest.main(["-v", __file__])
