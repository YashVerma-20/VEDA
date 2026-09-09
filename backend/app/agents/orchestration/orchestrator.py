from datetime import datetime
from typing import Dict, Any, List

from .schemas import OrchestrationRequest, OrchestrationResult, VehicleOrchestrationRequest

# Import completed agents and their schemas
from agents.monitoring.agent import MonitoringAgent
from agents.monitoring.schemas import MonitoringInput

from agents.diagnostics.agent import DiagnosticsAgent
from agents.diagnostics.schemas import DiagnosticsInput

from agents.prognostics.agent import PrognosticsAgent
from agents.prognostics.schemas import PrognosticsInput

from agents.maintenance_planning.agent import MaintenancePlanningAgent
from agents.maintenance_planning.schemas import MaintenancePlanningInput

from agents.spare_parts.agent import SparePartsAgent
from agents.spare_parts.schemas import SparePartsInput

from agents.fleet_readiness.agent import FleetReadinessAgent
from agents.fleet_readiness.schemas import FleetReadinessInput, VehicleReadinessInput


class VedaOrchestrator:
    """
    Coordinates the execution of the six Agentic AI layers.
    Does NOT make business decisions. Does NOT recalculate models.
    """
    
    def __init__(self):
        # Register the completed agents securely
        self.monitoring_agent = MonitoringAgent()
        self.diagnostics_agent = DiagnosticsAgent()
        self.prognostics_agent = PrognosticsAgent()
        self.maintenance_agent = MaintenancePlanningAgent()
        self.spare_parts_agent = SparePartsAgent()
        self.fleet_readiness_agent = FleetReadinessAgent()
        
    def process(self, request: OrchestrationRequest) -> OrchestrationResult:
        execution_trace = []
        vehicle_results = {}
        error_state = None
        fleet_id = request.fleet_id if request.fleet_id else "DEFAULT_FLEET"
        
        fleet_readiness_input_vehicles = {}
        
        for v_req in request.vehicles:
            trace_id = f"exec_{v_req.vehicle_id}_{datetime.now().timestamp()}"
            v_trace = {"vehicle_id": v_req.vehicle_id, "steps": []}
            
            try:
                # 1. Monitoring
                m_input = MonitoringInput(
                    vehicle_id=v_req.vehicle_id,
                    vehicle_class=v_req.vehicle_class,
                    timestamp=datetime.now(),
                    telemetry=v_req.telemetry or {},
                    rf_abnormal_probability=v_req.rf_abnormal_probability,
                    rf_abnormal_prediction=v_req.rf_abnormal_prediction
                )
                m_res = self.monitoring_agent.process(m_input)
                v_trace["steps"].append({"agent": "MonitoringAgent", "status": m_res.status})
                
                # 2. Diagnostics
                d_input = DiagnosticsInput(
                    monitoring_result=m_res,
                    telemetry=v_req.telemetry or {},
                    rf_abnormal_class=v_req.rf_abnormal_class,
                    fault_codes=v_req.fault_codes or []
                )
                d_res = self.diagnostics_agent.process(d_input)
                v_trace["steps"].append({"agent": "DiagnosticsAgent", "status": d_res.status})
                
                # 3. Prognostics
                p_input = PrognosticsInput(
                    monitoring_result=m_res,
                    diagnostics_result=d_res,
                    lstm_rul_hours=v_req.lstm_rul_hours,
                    xgb_rul_hours=v_req.xgb_rul_hours,
                    fusion_rul_hours=v_req.fusion_rul_hours
                )
                p_res = self.prognostics_agent.process(p_input)
                v_trace["steps"].append({"agent": "PrognosticsAgent", "status": p_res.status})
                
                # 4. Maintenance Planning
                mp_input = MaintenancePlanningInput(
                    monitoring_result=m_res,
                    diagnostics_result=d_res,
                    prognostics_result=p_res
                )
                mp_res = self.maintenance_agent.process(mp_input)
                v_trace["steps"].append({"agent": "MaintenancePlanningAgent", "status": mp_res.status})
                
                # 5. Spare Parts
                sp_input = SparePartsInput(maintenance_plan=mp_res)
                sp_res = self.spare_parts_agent.process(sp_input)
                v_trace["steps"].append({"agent": "SparePartsAgent", "status": sp_res.availability_status})
                
                # Store vehicle pipeline results
                vehicle_results[v_req.vehicle_id] = {
                    "monitoring": m_res.model_dump(mode="json"),
                    "diagnostics": d_res.model_dump(mode="json"),
                    "prognostics": p_res.model_dump(mode="json"),
                    "maintenance_plan": mp_res.model_dump(mode="json"),
                    "spare_parts": sp_res.model_dump(mode="json")
                }
                
                # Prepare for fleet readiness
                fleet_readiness_input_vehicles[v_req.vehicle_id] = VehicleReadinessInput(
                    monitoring_result=m_res,
                    diagnostics_result=d_res,
                    prognostics_result=p_res,
                    maintenance_plan=mp_res,
                    spare_parts_requirement=sp_res
                )
                
            except Exception as e:
                v_trace["steps"].append({"agent": "UNKNOWN", "status": "ERROR", "error": str(e)})
                error_state = f"Failure during vehicle {v_req.vehicle_id} processing."
                
            execution_trace.append(v_trace)
            
        # 6. Fleet Readiness (always run on aggregated data)
        try:
            f_input = FleetReadinessInput(
                fleet_id=fleet_id,
                vehicles=fleet_readiness_input_vehicles
            )
            f_res = self.fleet_readiness_agent.process(f_input)
            execution_trace.append({"agent": "FleetReadinessAgent", "status": f_res.readiness_status})
        except Exception as e:
            f_res = None
            execution_trace.append({"agent": "FleetReadinessAgent", "status": "ERROR", "error": str(e)})
            error_state = "Failure during fleet readiness processing."
            
        return OrchestrationResult(
            request_id=request.request_id,
            timestamp=datetime.now(),
            status="SUCCESS" if not error_state else "PARTIAL_SUCCESS" if vehicle_results else "FAILURE",
            fleet_status=f_res,
            vehicle_results=vehicle_results,
            execution_trace=execution_trace,
            error_state=error_state
        )
