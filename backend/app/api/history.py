from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from db.models import Vehicle, InferenceRun
from schemas.history import VehicleHistoryResponse, InferenceRunHistory

router = APIRouter()

@router.get("/vehicles", response_model=List[VehicleHistoryResponse])
def get_vehicles(db: Session = Depends(get_db)):
    """Retrieve list of all vehicles."""
    vehicles = db.query(Vehicle).all()
    return vehicles

@router.get("/vehicles/{vehicle_id}", response_model=VehicleHistoryResponse)
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """Retrieve specific vehicle details."""
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.get("/vehicles/{vehicle_id}/inferences", response_model=List[InferenceRunHistory])
def get_vehicle_inferences(vehicle_id: str, db: Session = Depends(get_db)):
    """Retrieve inference history for a specific vehicle, ordered newest first."""
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    inferences = (
        db.query(InferenceRun)
        .filter(InferenceRun.vehicle_id == vehicle_id)
        .order_by(InferenceRun.created_at.desc())
        .all()
    )
    return inferences

@router.get("/inferences/{inference_id}", response_model=InferenceRunHistory)
def get_inference(inference_id: int, db: Session = Depends(get_db)):
    """Retrieve specific inference run details."""
    inference = db.query(InferenceRun).filter(InferenceRun.id == inference_id).first()
    if not inference:
        raise HTTPException(status_code=404, detail="Inference run not found")
    return inference
