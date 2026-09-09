from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

from agents.monitoring.schemas import MonitoringResult
from agents.diagnostics.schemas import DiagnosticsResult
from agents.prognostics.schemas import PrognosticsResult

class MaintenancePlanningInput(BaseModel):
    monitoring_result: MonitoringResult
    diagnostics_result: DiagnosticsResult
    prognostics_result: PrognosticsResult
    
    model_config = ConfigDict(extra="forbid")

class MaintenancePlan(BaseModel):
    vehicle_id: str
    timestamp: datetime
    recommended_action: str
    priority: str
    reason: str
    estimated_time_frame_hours: Optional[float] = None
    maintenance_status: str
    constraints_missing_info: list[str] = Field(default_factory=list)
    status: str
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)
