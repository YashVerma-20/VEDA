from datetime import datetime
from typing import Dict, Any

from .schemas import DiagnosticsInput, DiagnosticsResult

class DiagnosticsAgent:
    """
    Diagnostics Agent for VEDA.
    Responsible for interpreting abnormal monitoring results and telemetry to determine likely causes.
    Does NOT calculate RUL or plan maintenance.
    """
    
    def __init__(self):
        self.agent_name = "DiagnosticsAgent_v1"
        
    def process(self, input_data: DiagnosticsInput) -> DiagnosticsResult:
        mr = input_data.monitoring_result
        
        # 1. Error handling / Invalid Input
        if mr.status in ["UNSUPPORTED_VEHICLE", "INSUFFICIENT_DATA"]:
            return self._build_result(
                mr,
                problem="UNKNOWN",
                evidence=[],
                cause="Insufficient upstream data or unsupported vehicle.",
                action="AWAIT_VALID_DATA",
                status="INSUFFICIENT_EVIDENCE"
            )
            
        # 2. Conflicting Evidence
        # For instance, if RF says normal but fault codes exist, or vice versa if we had complex rules.
        if not mr.abnormal_detected and input_data.fault_codes:
            return self._build_result(
                mr,
                problem="CONFLICT",
                evidence=["fault_codes_present", "rf_normal"],
                cause="Conflicting evidence between telemetry/faults and RF model.",
                action="HUMAN_REVIEW",
                status="CONFLICT"
            )
            
        # 3. Normal state (No abnormality detected)
        if not mr.abnormal_detected:
            return self._build_result(
                mr,
                problem="NONE",
                evidence=["rf_normal"],
                cause="Vehicle operating normally.",
                action="CONTINUE_MONITORING",
                status="SUCCESS"
            )
            
        # 4. Abnormal State Handling
        # We only diagnose what we have evidence for.
        evidence_sensors = []
        probable_cause = "Unknown subsystem affected."
        problem = "Abnormal condition detected"
        confidence = None
        
        if mr.source_model_info and "rf_probability" in mr.source_model_info:
            confidence = mr.source_model_info["rf_probability"]
            
        # If RF classification label is provided, we use it as evidence.
        if input_data.rf_abnormal_class:
            evidence_sensors.append(f"rf_class:{input_data.rf_abnormal_class}")
            probable_cause = f"Likely subsystem affected: {input_data.rf_abnormal_class}"
            problem = f"Abnormal condition in {input_data.rf_abnormal_class}"
            
        # If fault codes exist, we add them.
        if input_data.fault_codes:
            evidence_sensors.extend([f"fault:{fc}" for fc in input_data.fault_codes])
            probable_cause += " (Supported by fault codes)"
            
        # We don't invent specific thresholds here unless specified, so we just aggregate.
        if not evidence_sensors:
            evidence_sensors.append("rf_abnormal_prediction")
            
        return self._build_result(
            mr,
            problem=problem,
            evidence=evidence_sensors,
            cause=probable_cause,
            action="TRIGGER_MAINTENANCE_PLANNING",
            status="SUCCESS",
            confidence=confidence
        )

    def _build_result(self, mr, problem: str, evidence: list, cause: str, action: str, status: str, confidence: float = None) -> DiagnosticsResult:
        return DiagnosticsResult(
            vehicle_id=mr.vehicle_id,
            timestamp=mr.timestamp,
            problem_detected=problem,
            evidence_sensors=evidence,
            probable_cause=cause,
            confidence=confidence,
            next_diagnostic_action=action,
            status=status,
            execution_metadata={
                "agent_name": self.agent_name,
                "execution_timestamp": datetime.now().isoformat()
            }
        )
