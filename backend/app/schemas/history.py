from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class VehicleHistoryResponse(BaseModel):
    vehicle_id: str
    vehicle_class: str
    display_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InferenceResultHistory(BaseModel):
    rf_result: Optional[Dict[str, Any]] = None
    lstm_result: Optional[float] = None
    xgb_result: Optional[float] = None
    fusion_rul_hours: Optional[float] = None
    fusion_method: str

    class Config:
        from_attributes = True

class FleetReadinessHistory(BaseModel):
    readiness_status: str
    ready_count: int
    attention_count: int
    not_ready_count: int
    unknown_count: int

    class Config:
        from_attributes = True

class InferenceRunHistory(BaseModel):
    id: int
    vehicle_id: str
    vehicle_class: str
    timestep_count: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    inference_result: Optional[InferenceResultHistory] = None
    fleet_readiness: Optional[FleetReadinessHistory] = None

    class Config:
        from_attributes = True
