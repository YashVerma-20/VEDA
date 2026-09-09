from datetime import datetime
from typing import Dict, Any

from .schemas import MaintenancePlanningInput, MaintenancePlan

class MaintenancePlanningAgent:
    """
    Maintenance Planning Agent for VEDA.
    Responsible for recommending maintenance based on validated diagnostic/prognostic data.
    Does NOT execute maintenance, claim completion, or calculate RUL.
    """
    
    def __init__(self):
        self.agent_name = "MaintenancePlanningAgent_v1"
        
    def process(self, input_data: MaintenancePlanningInput) -> MaintenancePlan:
        mr = input_data.monitoring_result
        dr = input_data.diagnostics_result
        pr = input_data.prognostics_result
        
        status = "SUCCESS"
        recommended_action = "No action required."
        priority = "UNKNOWN"
        reason = "System operating normally."
        maintenance_status = "UNKNOWN"
        constraints = []
        
        # 1. Input Validation & Error Handling
        if mr.status in ["UNSUPPORTED_VEHICLE", "INSUFFICIENT_DATA"] or \
           dr.status in ["INSUFFICIENT_EVIDENCE", "CONFLICT"] or \
           pr.status in ["INVALID", "CONFLICT"]:
               
            return self._build_result(
                mr,
                action="AWAIT_VALID_DATA",
                priority="UNKNOWN",
                reason="Upstream data is insufficient, invalid, or conflicting.",
                m_status="UNKNOWN",
                constraints=["Upstream conflict or missing data prevents planning."],
                status="CONFLICT"
            )
            
        # 2. Evaluate Diagnostics & Prognostics
        if dr.problem_detected != "NONE":
            # A problem exists. Since no numerical thresholds are approved to invent here,
            # we rely on the Diagnostics Agent's recommendation to trigger planning.
            reason = f"Diagnostics flagged: {dr.problem_detected}. "
            
            if pr.status == "AVAILABLE" and pr.fusion_rul_hours is not None:
                reason += f"Prognostic RUL estimate: {pr.fusion_rul_hours} hours."
            elif pr.status == "PARTIAL_MODELS_AVAILABLE":
                reason += "Partial prognostic data available (Fusion unavailable)."
                
            recommended_action = f"RECOMMENDED: Inspect and service {dr.probable_cause}"
            maintenance_status = "RECOMMENDED"
            constraints.append("Requires approved policy information to assign priority.")
            constraints.append("Requires Spare Parts Agent to determine part availability.")
            
        else:
            # No current diagnostic problem.
            # If prognostics show degradation but no immediate diagnostic fault:
            if pr.degradation_trend == "OBSERVED_DEGRADATION":
                recommended_action = "RECOMMENDED: Schedule routine preventative inspection."
                maintenance_status = "RECOMMENDED"
                reason = "Prognostics indicates degradation trend, though no acute fault diagnosed."
                constraints.append("Requires approved preventative maintenance policy.")
            else:
                maintenance_status = "UNKNOWN"  # No maintenance planned/recommended
                
        # 3. Prevent Hallucination of Completion
        # We enforce that maintenance_status can never be 'COMPLETED'.
        if maintenance_status == "COMPLETED":
            maintenance_status = "UNKNOWN"
            
        return self._build_result(
            mr,
            action=recommended_action,
            priority=priority,
            reason=reason,
            m_status=maintenance_status,
            constraints=constraints,
            status=status
        )

    def _build_result(self, mr, action: str, priority: str, reason: str, m_status: str, constraints: list, status: str) -> MaintenancePlan:
        return MaintenancePlan(
            vehicle_id=mr.vehicle_id,
            timestamp=mr.timestamp,
            recommended_action=action,
            priority=priority,
            reason=reason,
            estimated_time_frame_hours=None,  # Do not invent repair times
            maintenance_status=m_status,
            constraints_missing_info=constraints,
            status=status,
            execution_metadata={
                "agent_name": self.agent_name,
                "execution_timestamp": datetime.now().isoformat()
            }
        )
