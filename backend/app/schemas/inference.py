from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class InferenceRequest(BaseModel):
    vehicle_id: str
    vehicle_class: str
    telemetry: List[Dict[str, Any]] = Field(..., description="An ordered sequence of timestamped vehicle telemetry records")
    
    # Optionally, we can define request properties, but the prompt says:
    # "The telemetry input must support the 30-timestep requirement of the frozen prognostic models"
    # "The last 30 sequential timesteps must correspond to the same vehicle."
