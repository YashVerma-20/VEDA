from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

from agents.monitoring.schemas import MonitoringResult
from agents.diagnostics.schemas import DiagnosticsResult

class PrognosticsInput(BaseModel):
    monitoring_result: MonitoringResult
    diagnostics_result: Optional[DiagnosticsResult] = None
    lstm_rul_hours: Optional[float] = None
    xgb_rul_hours: Optional[float] = None
    fusion_rul_hours: Optional[float] = None
    
    model_config = ConfigDict(extra="forbid")

class PrognosticsResult(BaseModel):
    vehicle_id: str
    timestamp: datetime
    fusion_rul_hours: Optional[float] = None
    lstm_rul_hours: Optional[float] = None
    xgb_rul_hours: Optional[float] = None
    degradation_trend: str
    risk_level: str
    status: str
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)
