from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import pandas as pd
import traceback
import logging

from schemas.inference import InferenceRequest
from services.ml_inference_service import MLInferenceService
from agents.orchestration.orchestrator import VedaOrchestrator
from agents.orchestration.schemas import OrchestrationRequest, OrchestrationResult
from sqlalchemy.orm import Session
from db.session import get_db
from services.persistence_service import PersistenceService

router = APIRouter()
logger = logging.getLogger(__name__)

# Lazy initialization / caching of services
_ml_service = None
_orchestrator = None

def get_ml_service() -> MLInferenceService:
    global _ml_service
    if _ml_service is None:
        try:
            _ml_service = MLInferenceService()
        except Exception as e:
            logger.error(f"Failed to initialize MLInferenceService: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal ML Service Initialization Error"
            )
    return _ml_service

def get_orchestrator() -> VedaOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        try:
            _orchestrator = VedaOrchestrator()
        except Exception as e:
            logger.error(f"Failed to initialize VedaOrchestrator: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Orchestrator Initialization Error"
            )
    return _orchestrator

@router.post("/", response_model=OrchestrationResult)
def run_inference(
    request: InferenceRequest,
    ml_service: MLInferenceService = Depends(get_ml_service),
    orchestrator: VedaOrchestrator = Depends(get_orchestrator),
    db: Session = Depends(get_db)
):
    """
    Execute End-to-End VEDA ML Inference & Agentic Orchestration for a given vehicle.
    """
    # 1. Validate vehicle class (must match known contracts)
    valid_classes = {"TANK", "LOGISTIC TRUCK", "OFFICER VEHICLE"}
    if request.vehicle_class.upper() not in valid_classes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid vehicle_class. Supported classes are: {', '.join(valid_classes)}"
        )
        
    # 2. Check telemetry sequence (must be numeric values ideally)
    if not request.telemetry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telemetry sequence cannot be empty."
        )
    
    # 3. Process telemetry via MLInferenceService
    try:
        df = pd.DataFrame(request.telemetry)
        
        # Vehicle class string handling based on Phase 6B logic (it handles uppercase checks)
        ml_req = ml_service.run_inference(
            vehicle_id=request.vehicle_id,
            vehicle_class=request.vehicle_class,
            telemetry_df=df
        )
    except Exception as e:
        logger.error(f"Error during ML inference: {str(e)}")
        # Note: structured error without exposing stack trace
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing telemetry sequence through ML pipeline."
        )
        
    # 4. Route through Orchestrator
    try:
        orch_req = OrchestrationRequest(
            request_id=f"REQ_{request.vehicle_id}",
            request_type="SINGLE_VEHICLE",
            fleet_id="DEFAULT_FLEET",
            vehicles=[ml_req]
        )
        result = orchestrator.process(orch_req)
        
        # 5. Persist the result
        try:
            PersistenceService.save_inference(db, request, result, request.vehicle_class.upper())
        except Exception as db_e:
            logger.error(f"Persistence error: {str(db_e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database persistence failed. Inference transaction rolled back."
            )
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during Orchestration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error orchestrating downstream agent execution."
        )
