from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, unique=True, index=True, nullable=False)
    vehicle_class = Column(String, nullable=False, index=True)
    display_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    inference_runs = relationship("InferenceRun", back_populates="vehicle", cascade="all, delete")

class InferenceRun(Base):
    __tablename__ = "inference_runs"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, ForeignKey("vehicles.vehicle_id"), nullable=False, index=True)
    vehicle_class = Column(String, nullable=False)
    timestep_count = Column(Integer, nullable=False)
    status = Column(String, nullable=False, index=True) # SUCCESS, UNKNOWN, FAILED
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    vehicle = relationship("Vehicle", back_populates="inference_runs")
    telemetry_records = relationship("TelemetryRecord", back_populates="inference_run", cascade="all, delete")
    inference_result = relationship("InferenceResult", back_populates="inference_run", uselist=False, cascade="all, delete")
    agent_results = relationship("AgentResult", back_populates="inference_run", cascade="all, delete")
    fleet_readiness = relationship("FleetReadiness", back_populates="inference_run", uselist=False, cascade="all, delete")

class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"
    id = Column(Integer, primary_key=True, index=True)
    inference_id = Column(Integer, ForeignKey("inference_runs.id"), nullable=False, index=True)
    vehicle_id = Column(String, nullable=False, index=True)
    timestep = Column(Integer, nullable=False)
    timestamp = Column(String, nullable=True)
    telemetry_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    inference_run = relationship("InferenceRun", back_populates="telemetry_records")

class InferenceResult(Base):
    __tablename__ = "inference_results"
    id = Column(Integer, primary_key=True, index=True)
    inference_id = Column(Integer, ForeignKey("inference_runs.id"), nullable=False, index=True)
    rf_result = Column(JSON, nullable=True)
    lstm_result = Column(Float, nullable=True)
    xgb_result = Column(Float, nullable=True)
    fusion_rul_hours = Column(Float, nullable=True)
    fusion_method = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    inference_run = relationship("InferenceRun", back_populates="inference_result")

class AgentResult(Base):
    __tablename__ = "agent_results"
    id = Column(Integer, primary_key=True, index=True)
    inference_id = Column(Integer, ForeignKey("inference_runs.id"), nullable=False, index=True)
    agent_name = Column(String, nullable=False, index=True)
    agent_status = Column(String, nullable=True)
    agent_output = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    inference_run = relationship("InferenceRun", back_populates="agent_results")

class FleetReadiness(Base):
    __tablename__ = "fleet_readiness"
    id = Column(Integer, primary_key=True, index=True)
    inference_id = Column(Integer, ForeignKey("inference_runs.id"), nullable=False, index=True)
    readiness_status = Column(String, nullable=False)
    ready_count = Column(Integer, nullable=False, default=0)
    attention_count = Column(Integer, nullable=False, default=0)
    not_ready_count = Column(Integer, nullable=False, default=0)
    unknown_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    inference_run = relationship("InferenceRun", back_populates="fleet_readiness")
