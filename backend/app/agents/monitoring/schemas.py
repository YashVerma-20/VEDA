from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class MonitoringInput(BaseModel):
    vehicle_id: str
    vehicle_class: str
    timestamp: datetime
    telemetry: Optional[Dict[str, float]] = Field(default_factory=dict)
    rf_abnormal_probability: Optional[float] = None
    rf_abnormal_prediction: Optional[int] = None
    
    # We explicitly forbid the following fields to ensure strict model-agent separation
    # Pydantic v2 handles this cleanly with extra='forbid'
    model_config = ConfigDict(extra="forbid")

class MonitoringResult(BaseModel):
    vehicle_id: str
    vehicle_class: str
    timestamp: datetime
    abnormal_detected: bool
    severity: str
    observed_findings: list[str] = Field(default_factory=list)
    source_model_info: Optional[Dict[str, Any]] = None
    status: str
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)
