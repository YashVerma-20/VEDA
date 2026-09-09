from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

from agents.fleet_readiness.schemas import FleetReadinessStatus

class VehicleOrchestrationRequest(BaseModel):
    vehicle_id: str
    vehicle_class: str
    telemetry: Optional[Dict[str, float]] = None
    rf_abnormal_class: Optional[str] = None
    rf_abnormal_probability: Optional[float] = None
    rf_abnormal_prediction: Optional[int] = None
    fault_codes: Optional[List[str]] = None
    lstm_rul_hours: Optional[float] = None
    xgb_rul_hours: Optional[float] = None
    fusion_rul_hours: Optional[float] = None
    
    model_config = ConfigDict(extra="forbid")

class OrchestrationRequest(BaseModel):
    request_id: str
    request_type: str  # "SINGLE_VEHICLE" or "FLEET"
    fleet_id: Optional[str] = None
    vehicles: List[VehicleOrchestrationRequest]
    
    model_config = ConfigDict(extra="forbid")

class OrchestrationResult(BaseModel):
    request_id: str
    timestamp: datetime
    status: str
    fleet_status: Optional[FleetReadinessStatus] = None
    vehicle_results: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    execution_trace: List[Dict[str, Any]] = Field(default_factory=dict)
    error_state: Optional[str] = None
