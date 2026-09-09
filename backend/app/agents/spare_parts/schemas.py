from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

from agents.maintenance_planning.schemas import MaintenancePlan

class SparePartsInput(BaseModel):
    maintenance_plan: MaintenancePlan
    
    model_config = ConfigDict(extra="forbid")

class SparePartsRequirement(BaseModel):
    vehicle_id: str
    timestamp: datetime
    maintenance_reference: str
    component: str
    part_identifier: str
    part_description: str
    quantity: Optional[int] = None
    inventory_status: str
    procurement_status: str
    availability_status: str
    reason: str
    source_information: Dict[str, Any] = Field(default_factory=dict)
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)
