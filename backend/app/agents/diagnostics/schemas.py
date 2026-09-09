from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

from agents.monitoring.schemas import MonitoringResult

class DiagnosticsInput(BaseModel):
    monitoring_result: MonitoringResult
    telemetry: Optional[Dict[str, float]] = Field(default_factory=dict)
    rf_abnormal_class: Optional[str] = None
    fault_codes: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(extra="forbid")

class DiagnosticsResult(BaseModel):
    vehicle_id: str
    timestamp: datetime
    problem_detected: str
    evidence_sensors: List[str] = Field(default_factory=list)
    probable_cause: str
    confidence: Optional[float] = None
    next_diagnostic_action: str
    status: str
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)
