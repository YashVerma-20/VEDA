from datetime import datetime
from typing import Dict, Any

from .schemas import MonitoringInput, MonitoringResult

class MonitoringAgent:
    """
    Monitoring Agent for VEDA.
    Responsible for observing incoming vehicle telemetry and available ML inference results.
    Does NOT calculate RUL or plan maintenance.
    """
    
    SUPPORTED_CLASSES = ["TANK", "LOGISTIC", "OFFICER"]
    
    def __init__(self):
        self.agent_name = "MonitoringAgent_v1"
        
    def process(self, input_data: MonitoringInput) -> MonitoringResult:
        findings = []
        abnormal = False
        severity = "NORMAL"
        status = "SUCCESS"
        
        # 1. Unknown / Unsupported vehicle isolation
        v_class = input_data.vehicle_class.upper()
        if v_class not in self.SUPPORTED_CLASSES:
            return MonitoringResult(
                vehicle_id=input_data.vehicle_id,
                vehicle_class=input_data.vehicle_class,
                timestamp=input_data.timestamp,
                abnormal_detected=False,
                severity="UNKNOWN",
                observed_findings=["Unsupported vehicle class."],
                status="UNSUPPORTED_VEHICLE",
                execution_metadata=self._metadata()
            )
            
        # 2. Missing Telemetry
        if not input_data.telemetry:
            return MonitoringResult(
                vehicle_id=input_data.vehicle_id,
                vehicle_class=input_data.vehicle_class,
                timestamp=input_data.timestamp,
                abnormal_detected=False,
                severity="UNKNOWN",
                observed_findings=["Missing telemetry data."],
                status="INSUFFICIENT_DATA",
                execution_metadata=self._metadata()
            )
            
        # 3. Missing RF Result
        if input_data.rf_abnormal_prediction is None:
            status = "UNAVAILABLE_RF"
            findings.append("Random Forest prediction unavailable.")
            severity = "UNKNOWN"
        else:
            # 4. Normal / Abnormal based on frozen RF Output
            if input_data.rf_abnormal_prediction == 1:
                abnormal = True
                severity = "WARNING"
                findings.append("RF abnormality classification triggered.")
            else:
                abnormal = False
                severity = "NORMAL"
                
        # 5. We do not invent thresholds for raw telemetry. We only report what was provided.
        source_info = {}
        if input_data.rf_abnormal_probability is not None:
            source_info["rf_probability"] = input_data.rf_abnormal_probability
            
        return MonitoringResult(
            vehicle_id=input_data.vehicle_id,
            vehicle_class=input_data.vehicle_class,
            timestamp=input_data.timestamp,
            abnormal_detected=abnormal,
            severity=severity,
            observed_findings=findings,
            source_model_info=source_info,
            status=status,
            execution_metadata=self._metadata()
        )
        
    def _metadata(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "execution_timestamp": datetime.now().isoformat()
        }
