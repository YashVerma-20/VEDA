from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

from agents.spare_parts.schemas import SparePartsRequirement
from agents.maintenance_planning.schemas import MaintenancePlan
from agents.prognostics.schemas import PrognosticsResult
from agents.diagnostics.schemas import DiagnosticsResult
from agents.monitoring.schemas import MonitoringResult

class VehicleReadinessInput(BaseModel):
    monitoring_result: Optional[MonitoringResult] = None
    diagnostics_result: Optional[DiagnosticsResult] = None
    prognostics_result: Optional[PrognosticsResult] = None
    maintenance_plan: Optional[MaintenancePlan] = None
    spare_parts_requirement: Optional[SparePartsRequirement] = None

class FleetReadinessInput(BaseModel):
    fleet_id: str
    vehicles: Dict[str, VehicleReadinessInput] = Field(default_factory=dict)
    
    model_config = ConfigDict(extra="forbid")

class FleetReadinessStatus(BaseModel):
    fleet_id: str
    timestamp: datetime
    readiness_status: str
    readiness_reason: str
    affected_vehicles: List[str] = Field(default_factory=list)
    vehicle_summaries: Dict[str, Any] = Field(default_factory=dict)
    source_information: Dict[str, Any] = Field(default_factory=dict)
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)
