from datetime import datetime
from typing import Dict, Any

from .schemas import SparePartsInput, SparePartsRequirement

class SparePartsAgent:
    """
    Spare Parts Agent for VEDA.
    Responsible for identifying required parts and inventory status.
    Currently, NO approved inventory data source or part mapping exists.
    Must NOT hallucinate part numbers, quantities, or stock levels.
    """
    
    def __init__(self):
        self.agent_name = "SparePartsAgent_v1"
        self.inventory_source_available = False
        self.part_mapping_available = False
        
    def process(self, input_data: SparePartsInput) -> SparePartsRequirement:
        mp = input_data.maintenance_plan
        
        # 1. Error handling / Upstream Invalid
        if mp.status in ["INVALID", "CONFLICT", "UNSUPPORTED_VEHICLE"]:
            return self._build_result(
                mp,
                component="UNKNOWN",
                part_id="UNKNOWN",
                desc="UNKNOWN",
                qty=None,
                inv_status="UNKNOWN",
                proc_status="UNKNOWN",
                avail_status="UNKNOWN",
                reason="Upstream maintenance plan is invalid or conflicting."
            )
            
        # 2. No maintenance recommended
        if mp.maintenance_status != "RECOMMENDED":
            return self._build_result(
                mp,
                component="NONE",
                part_id="NOT_APPLICABLE",
                desc="No maintenance recommended.",
                qty=None,
                inv_status="NOT_APPLICABLE",
                proc_status="NOT_APPLICABLE",
                avail_status="NOT_APPLICABLE",
                reason="No maintenance actions require spare parts at this time."
            )
            
        # 3. Maintenance Recommended, but NO Inventory or Mapping Sources
        # We explicitly refuse to hallucinate a part number or stock level.
        # We try to extract a generic component name from the upstream reason if it exists,
        # but the actual part identifier remains UNKNOWN.
        
        # Simplistic component extraction from maintenance reason/action if possible
        component = "UNKNOWN"
        if "Coolant Leak" in mp.recommended_action:
            component = "Cooling System"
        elif "Engine" in mp.recommended_action:
            component = "Engine"
            
        return self._build_result(
            mp,
            component=component,
            part_id="PART_MAPPING_UNAVAILABLE",
            desc="Specific part mapping is unavailable.",
            qty=None,  # Do not invent quantity (e.g. 1) without an explicit rule
            inv_status="UNKNOWN",
            proc_status="UNKNOWN",
            avail_status="UNKNOWN",
            reason="No approved inventory or part mapping source is available to determine part requirements."
        )

    def _build_result(self, mp, component: str, part_id: str, desc: str, qty: int, inv_status: str, proc_status: str, avail_status: str, reason: str) -> SparePartsRequirement:
        return SparePartsRequirement(
            vehicle_id=mp.vehicle_id,
            timestamp=mp.timestamp,
            maintenance_reference=mp.recommended_action,
            component=component,
            part_identifier=part_id,
            part_description=desc,
            quantity=qty,
            inventory_status=inv_status,
            procurement_status=proc_status,
            availability_status=avail_status,
            reason=reason,
            source_information={
                "inventory_source_available": self.inventory_source_available,
                "part_mapping_available": self.part_mapping_available
            },
            execution_metadata={
                "agent_name": self.agent_name,
                "execution_timestamp": datetime.now().isoformat()
            }
        )
