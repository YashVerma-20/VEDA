import math
from datetime import datetime
from typing import Dict, Any

from .schemas import PrognosticsInput, PrognosticsResult

class PrognosticsAgent:
    """
    Prognostics Agent for VEDA.
    Responsible for interpreting upstream ML prognostic outputs (Fusion RUL, LSTM, XGBoost).
    Does NOT calculate RUL or train models. Acts purely as an interpretation layer.
    """
    
    def __init__(self):
        self.agent_name = "PrognosticsAgent_v1"
        
    def _is_valid_rul(self, rul: float) -> bool:
        if rul is None:
            return False
        if math.isnan(rul) or math.isinf(rul):
            return False
        if rul < 0:
            return False
        return True
        
    def process(self, input_data: PrognosticsInput) -> PrognosticsResult:
        mr = input_data.monitoring_result
        dr = input_data.diagnostics_result
        
        # 1. Base initialization
        status = "SUCCESS"
        trend = "UNKNOWN"
        risk = "UNKNOWN"
        
        # 2. Extract and Validate ML predictions strictly
        fusion_rul = input_data.fusion_rul_hours if self._is_valid_rul(input_data.fusion_rul_hours) else None
        lstm_rul = input_data.lstm_rul_hours if self._is_valid_rul(input_data.lstm_rul_hours) else None
        xgb_rul = input_data.xgb_rul_hours if self._is_valid_rul(input_data.xgb_rul_hours) else None
        
        # 3. Check for missing prognostic output
        if fusion_rul is None and lstm_rul is None and xgb_rul is None:
            status = "UNAVAILABLE"
            trend = "UNKNOWN"
            risk = "UNKNOWN"
        elif fusion_rul is not None:
            status = "AVAILABLE"
            trend = "OBSERVED_DEGRADATION" if dr and dr.problem_detected != "NONE" else "STABLE"
            risk = "WARNING" if dr and dr.status == "SUCCESS" and dr.problem_detected != "NONE" else "NORMAL"
        else:
            # We have some models but not Fusion. We DO NOT fabricate a fusion RUL.
            status = "PARTIAL_MODELS_AVAILABLE"
            trend = "UNKNOWN"
            risk = "UNKNOWN"
            
        # 4. We do not invent thresholds (e.g. "if RUL < 50 hours").
        # If upstream diagnostics says there is a conflict or insufficient data, we carry that risk forward.
        if mr.status in ["UNSUPPORTED_VEHICLE", "INSUFFICIENT_DATA"]:
            status = "INVALID"
            risk = "UNKNOWN"
            trend = "UNKNOWN"
            
        if dr and dr.status == "CONFLICT":
            status = "CONFLICT"
            risk = "UNKNOWN"
            
        return PrognosticsResult(
            vehicle_id=mr.vehicle_id,
            timestamp=mr.timestamp,
            fusion_rul_hours=fusion_rul,
            lstm_rul_hours=lstm_rul,
            xgb_rul_hours=xgb_rul,
            degradation_trend=trend,
            risk_level=risk,
            status=status,
            execution_metadata={
                "agent_name": self.agent_name,
                "execution_timestamp": datetime.now().isoformat()
            }
        )
