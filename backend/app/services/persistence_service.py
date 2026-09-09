import logging
from sqlalchemy.orm import Session
from datetime import datetime
from db.models import Vehicle, InferenceRun, TelemetryRecord, InferenceResult, AgentResult, FleetReadiness
from schemas.inference import InferenceRequest
from agents.orchestration.schemas import OrchestrationResult

logger = logging.getLogger(__name__)

class PersistenceService:
    @staticmethod
    def save_inference(db: Session, request: InferenceRequest, result: OrchestrationResult, vehicle_class: str) -> None:
        """
        Persists the inference request and result atomically.
        Does not mutate the result or perform ML calculations.
        """
        try:
            # 1. Create or get Vehicle
            vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == request.vehicle_id).first()
            if not vehicle:
                vehicle = Vehicle(
                    vehicle_id=request.vehicle_id,
                    vehicle_class=vehicle_class,
                    display_name=f"{vehicle_class} {request.vehicle_id}"
                )
                db.add(vehicle)
                try:
                    db.flush()
                except Exception as e:
                    import sqlalchemy
                    if isinstance(e, sqlalchemy.exc.IntegrityError):
                        db.rollback()
                        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == request.vehicle_id).first()
                    else:
                        raise e
            
            # Determine fusion method based on vehicle class
            fusion_method = "1.00 × XGBoost" if vehicle_class.upper() == "TANK" else "0.30 × LSTM + 0.70 × XGBoost"
            
            # Determine overall status based on readiness or UNKNOWN handling
            status = result.fleet_status.readiness_status
            
            # 2. Create InferenceRun
            run = InferenceRun(
                vehicle_id=vehicle.vehicle_id,
                vehicle_class=vehicle_class,
                timestep_count=len(request.telemetry),
                status=status,
                completed_at=datetime.utcnow()
            )
            db.add(run)
            db.flush()
            
            # 3. Store Telemetry
            for idx, record in enumerate(request.telemetry):
                tr = TelemetryRecord(
                    inference_id=run.id,
                    vehicle_id=vehicle.vehicle_id,
                    timestep=idx,
                    timestamp=record.get("timestamp"),
                    telemetry_json=record
                )
                db.add(tr)
                
            # 4. Store Results (from vehicle_results dict)
            veh_res = result.vehicle_results.get(request.vehicle_id)
            if veh_res:
                # InferenceResult
                prog = veh_res.get("prognostics", {})
                mon = veh_res.get("monitoring", {})
                ir = InferenceResult(
                    inference_id=run.id,
                    rf_result={"abnormal_detected": mon.get("abnormal_detected"), "severity_score": mon.get("severity_score")},
                    lstm_result=prog.get("lstm_rul_hours"),
                    xgb_result=prog.get("xgb_rul_hours"),
                    fusion_rul_hours=prog.get("fusion_rul_hours"),
                    fusion_method=fusion_method
                )
                db.add(ir)
                
                # Agent Results
                agents = [
                    ("monitoring", mon),
                    ("diagnostics", veh_res.get("diagnostics", {})),
                    ("prognostics", prog),
                    ("maintenance_planning", veh_res.get("maintenance_planning", {})),
                    ("spare_parts", veh_res.get("spare_parts", {}))
                ]
                
                for agent_name, out in agents:
                    ar = AgentResult(
                        inference_id=run.id,
                        agent_name=agent_name,
                        agent_output=out
                    )
                    db.add(ar)
                    
            # Fleet Readiness
            fs = result.fleet_status
            if fs:
                counts = {"READY": 0, "ATTENTION": 0, "NOT_READY": 0, "UNKNOWN": 0}
                
                # Extract from dictionary if available, else count from summaries
                if isinstance(fs, dict):
                    readiness_status = fs.get("readiness_status", "UNKNOWN")
                    ready_c = fs.get("ready_count", 0)
                    attn_c = fs.get("attention_count", 0)
                    nr_c = fs.get("not_ready_count", 0)
                    unk_c = fs.get("unknown_count", 0)
                else:
                    readiness_status = getattr(fs, "readiness_status", "UNKNOWN")
                    # Try to extract counts from source_information if available
                    source_info = getattr(fs, "source_information", {})
                    metrics = source_info.get("metrics", {}) if isinstance(source_info, dict) else {}
                    if isinstance(metrics, dict) and "counts" in metrics:
                        for k, v in metrics["counts"].items():
                            if k in counts:
                                counts[k] = v
                    else:
                        # Fallback to counting from summaries
                        summaries = getattr(fs, "vehicle_summaries", {})
                        for v_stat in summaries.values():
                            if isinstance(v_stat, dict):
                                status_val = v_stat.get("vehicle_readiness_status")
                                if status_val in counts:
                                    counts[status_val] += 1
                            elif isinstance(v_stat, str) and v_stat in counts:
                                counts[v_stat] += 1
                    
                    ready_c = getattr(fs, "ready_count", counts["READY"])
                    attn_c = getattr(fs, "attention_count", counts["ATTENTION"])
                    nr_c = getattr(fs, "not_ready_count", counts["NOT_READY"])
                    unk_c = getattr(fs, "unknown_count", counts["UNKNOWN"])

                if isinstance(readiness_status, dict):
                    readiness_status = str(readiness_status)
                    
                fr = FleetReadiness(
                    inference_id=run.id,
                    readiness_status=readiness_status,
                    ready_count=ready_c,
                    attention_count=attn_c,
                    not_ready_count=nr_c,
                    unknown_count=unk_c
                )
                db.add(fr)
            
            # Commit transaction
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"PersistenceService failed to save inference: {str(e)}")
            raise e
