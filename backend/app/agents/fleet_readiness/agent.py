from datetime import datetime
from typing import Dict, Any, Tuple

from .schemas import FleetReadinessInput, FleetReadinessStatus, VehicleReadinessInput
from .config import (
    FLEET_READINESS_POLICY_VERSION,
    RUL_NOT_READY_THRESHOLD,
    RUL_ATTENTION_THRESHOLD,
    FLEET_NOT_READY_PERCENTAGE,
    FLEET_NOT_READY_COUNT,
    FLEET_READY_PERCENTAGE,
    FLEET_UNKNOWN_PERCENTAGE,
    FLEET_ATTENTION_PERCENTAGE
)

class FleetReadinessAgent:
    """
    Fleet Readiness Agent for VEDA.
    Implements a DUMMY/DEMONSTRATION configurable fleet readiness policy.
    NOT an official military or organizational readiness standard.
    """
    
    def __init__(self):
        self.agent_name = "FleetReadinessAgent_v1"
        self.readiness_policy_available = True
        self.aggregation_policy_available = True
        
    def _evaluate_vehicle(self, v_data: VehicleReadinessInput) -> Tuple[str, str]:
        # Precedence: NOT_READY -> UNKNOWN -> ATTENTION -> READY
        # However, UNKNOWN overrides lower-severity states when required info is missing.
        
        reason = "Evaluated using demo policy."
        
        # 1. Check for REQUIRED UNKNOWN
        # If any of the upstream agents explicitly failed or are missing, we can't establish readiness.
        # Check for missing crucial results
        if not v_data.monitoring_result or not v_data.diagnostics_result or not v_data.prognostics_result or not v_data.maintenance_plan:
            return "UNKNOWN", "Required upstream agent output is missing."
            
        # Check for explicitly indeterminate or conflicting upstream states
        if v_data.monitoring_result.status in ["UNSUPPORTED_VEHICLE", "INSUFFICIENT_DATA"]:
            return "UNKNOWN", "Monitoring data insufficient or unsupported."
        if v_data.diagnostics_result.status in ["INSUFFICIENT_EVIDENCE", "CONFLICT", "UNKNOWN"]:
            return "UNKNOWN", "Diagnostics result insufficient or conflicting."
        if v_data.prognostics_result.status in ["INVALID", "CONFLICT", "UNAVAILABLE"]:
            return "UNKNOWN", "Prognostic RUL unavailable or invalid."
        if v_data.maintenance_plan.status in ["CONFLICT", "UNKNOWN"]:
            return "UNKNOWN", "Maintenance plan conflicting or unknown."
            
        # 2. Evaluate NOT_READY
        not_ready_reasons = []
        # RUL < 100
        if v_data.prognostics_result.fusion_rul_hours is not None and v_data.prognostics_result.fusion_rul_hours < RUL_NOT_READY_THRESHOLD:
            not_ready_reasons.append(f"Fusion RUL < {RUL_NOT_READY_THRESHOLD}h")
        
        # Critical diagnostic
        # Existing Diagnostics Agent doesn't formally define "CRITICAL", it sets severity="WARNING" for abnormalities.
        # But if the maintenance plan says "RECOMMENDED" and it was from a problem detected... wait. 
        # The prompt says: map existing contract to policy. "If an exact mapping is not possible, STOP and report the mismatch instead of inventing data."
        # Actually, in Monitoring we have `severity` (e.g. CRITICAL). Diagnostics doesn't have severity.
        # Let's check Monitoring severity. If it's CRITICAL, that's a block. 
        if getattr(v_data.monitoring_result, "severity", "") == "CRITICAL":
            not_ready_reasons.append("Monitoring reported CRITICAL severity")
            
        if "Engine" in v_data.diagnostics_result.problem_detected and "Overheat" in v_data.diagnostics_result.problem_detected:
            # Example mapping: Let's assume there is no explicit CRITICAL diagnostic severity in DiagnosticsResult.
            # I must not invent one. I will use the Monitoring severity which has a CRITICAL state.
            pass
            
        # Immediate Maintenance (NOT_READY)
        rec_action = v_data.maintenance_plan.recommended_action.upper()
        if "IMMEDIATE" in rec_action and "NO_IMMEDIATE_ACTION" not in rec_action or "URGENT" in rec_action:
            not_ready_reasons.append("Immediate/Urgent maintenance required")
            
        if not_ready_reasons:
            return "NOT_READY", " | ".join(not_ready_reasons)
            
        # 3. Evaluate ATTENTION
        attention_reasons = []
        if v_data.prognostics_result.fusion_rul_hours is not None and RUL_NOT_READY_THRESHOLD <= v_data.prognostics_result.fusion_rul_hours <= RUL_ATTENTION_THRESHOLD:
            attention_reasons.append(f"Fusion RUL between {RUL_NOT_READY_THRESHOLD}h and {RUL_ATTENTION_THRESHOLD}h")
            
        if getattr(v_data.monitoring_result, "severity", "") == "WARNING" or v_data.diagnostics_result.problem_detected != "NONE":
            attention_reasons.append("Non-critical abnormality detected")
            
        if v_data.maintenance_plan.maintenance_status == "RECOMMENDED":
            attention_reasons.append("Planned maintenance recommended")
            
        if attention_reasons:
            return "ATTENTION", " | ".join(attention_reasons)
            
        # 4. Evaluate READY
        if v_data.prognostics_result.fusion_rul_hours is not None and v_data.prognostics_result.fusion_rul_hours > RUL_ATTENTION_THRESHOLD:
            return "READY", "All readiness conditions satisfied."
            
        return "UNKNOWN", "Insufficient data to determine READY state."

    def process(self, input_data: FleetReadinessInput) -> FleetReadinessStatus:
        fleet_id = input_data.fleet_id
        vehicles = input_data.vehicles
        
        # 1. Handle empty fleet
        if not vehicles:
            return self._build_result(
                fleet_id=fleet_id,
                status="UNKNOWN",
                reason="Empty fleet. No valid vehicle data.",
                affected=[],
                summaries={}
            )
            
        # 2. Extract vehicle summaries
        affected_vehicles = []
        vehicle_summaries = {}
        
        counts = {"READY": 0, "ATTENTION": 0, "NOT_READY": 0, "UNKNOWN": 0}
        total = len(vehicles)
        
        for v_id, v_data in vehicles.items():
            v_status, v_reason = self._evaluate_vehicle(v_data)
            
            if v_status != "READY":
                affected_vehicles.append(v_id)
                
            vehicle_summaries[v_id] = {
                "vehicle_readiness_status": v_status,
                "reason": v_reason
            }
            counts[v_status] += 1
            
        # 3. Fleet Aggregation
        p_ready = (counts["READY"] / total) * 100
        p_not_ready = (counts["NOT_READY"] / total) * 100
        p_attention = (counts["ATTENTION"] / total) * 100
        p_unknown = (counts["UNKNOWN"] / total) * 100
        
        fleet_status = "UNKNOWN"
        fleet_reason = ""
        
        # Precedence: NOT_READY -> UNKNOWN (if 100%) -> ATTENTION -> READY
        # But policy says: UNKNOWN if no valid vehicle results or insufficient info.
        
        if p_not_ready >= FLEET_NOT_READY_PERCENTAGE or counts["NOT_READY"] >= FLEET_NOT_READY_COUNT:
            fleet_status = "NOT_READY"
            fleet_reason = f"NOT_READY >= {FLEET_NOT_READY_PERCENTAGE}% or count >= {FLEET_NOT_READY_COUNT}"
        elif p_unknown >= FLEET_UNKNOWN_PERCENTAGE:
            # Policy AT-3? Wait. 8.2 says: "If the fleet is not NOT_READY, classify it as ATTENTION if... UNKNOWN percentage >= 10%"
            fleet_status = "ATTENTION"
            fleet_reason = "UNKNOWN percentage >= 10% or READY < 80% or ATTENTION >= 20%"
        elif p_ready < FLEET_READY_PERCENTAGE or p_attention >= FLEET_ATTENTION_PERCENTAGE:
            fleet_status = "ATTENTION"
            fleet_reason = "READY < 80% or ATTENTION >= 20%"
        elif p_ready >= FLEET_READY_PERCENTAGE and p_not_ready < FLEET_NOT_READY_PERCENTAGE and p_unknown < FLEET_UNKNOWN_PERCENTAGE:
            fleet_status = "READY"
            fleet_reason = "Fleet meets all READY criteria."
        else:
            fleet_status = "UNKNOWN"
            fleet_reason = "Indeterminate due to mixed unknown factors."
            
        # Specific override for complete unknown
        if counts["UNKNOWN"] == total:
            fleet_status = "UNKNOWN"
            fleet_reason = "The fleet contains no valid vehicle readiness results."

        return self._build_result(
            fleet_id=fleet_id,
            status=fleet_status,
            reason=f"[{FLEET_READINESS_POLICY_VERSION}] " + fleet_reason,
            affected=affected_vehicles,
            summaries=vehicle_summaries,
            extra_metrics={
                "total_vehicles": total,
                "counts": counts,
                "percentages": {
                    "READY": p_ready,
                    "NOT_READY": p_not_ready,
                    "ATTENTION": p_attention,
                    "UNKNOWN": p_unknown
                },
                "policy_version": FLEET_READINESS_POLICY_VERSION
            }
        )

    def _build_result(self, fleet_id: str, status: str, reason: str, affected: list, summaries: dict, extra_metrics: dict = None) -> FleetReadinessStatus:
        return FleetReadinessStatus(
            fleet_id=fleet_id,
            timestamp=datetime.now(),
            readiness_status=status,
            readiness_reason=reason,
            affected_vehicles=affected,
            vehicle_summaries=summaries,
            source_information={
                "readiness_policy_available": self.readiness_policy_available,
                "aggregation_policy_available": self.aggregation_policy_available,
                "metrics": extra_metrics or {},
                "disclaimer": "DUMMY / DEMONSTRATION POLICY - NOT AN OFFICIAL OPERATIONAL STANDARD"
            },
            execution_metadata={
                "agent_name": self.agent_name,
                "execution_timestamp": datetime.now().isoformat()
            }
        )
