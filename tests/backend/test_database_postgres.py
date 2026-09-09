import pytest
import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "app")))

from db.models import Base, Vehicle, InferenceRun, TelemetryRecord, InferenceResult, AgentResult, FleetReadiness
import uuid

from dotenv import load_dotenv
load_dotenv()

def get_postgres_engine():
    # Attempt to connect to PostgreSQL.
    db_url = os.environ.get("DATABASE_URL", "postgresql://user:password@127.0.0.1:5433/veda")
    
    # We do not want to test against SQLite in this suite.
    if db_url.startswith("sqlite"):
        return None
        
    engine = create_engine(db_url)
    try:
        # Check connection
        with engine.connect() as conn:
            pass
        return engine
    except sqlalchemy.exc.OperationalError:
        return None

@pytest.fixture(scope="module")
def postgres_db():
    engine = get_postgres_engine()
    if engine is None:
        pytest.fail("PostgreSQL engine could not be instantiated; blocked by environment or incorrect configuration.")
        
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    
    # We will NOT drop_all because it destroys the schema for other tests.

def test_postgres_tables_exist(postgres_db):
    """Test that all required tables are created in the PostgreSQL database schema."""
    assert postgres_db.query(Vehicle).count() >= 0
    assert postgres_db.query(InferenceRun).count() >= 0
    assert postgres_db.query(TelemetryRecord).count() >= 0
    assert postgres_db.query(InferenceResult).count() >= 0
    assert postgres_db.query(AgentResult).count() >= 0
    assert postgres_db.query(FleetReadiness).count() >= 0

def test_postgres_crud_flow(postgres_db):
    """
    Test a full CRUD flow inside PostgreSQL mimicking an inference save.
    DATABASE TEST FIXTURES ONLY. NOT LIVE TELEMETRY.
    """
    v_id = f"TEST-PG-{uuid.uuid4().hex[:8]}"
    v = Vehicle(vehicle_id=v_id, vehicle_class="TANK", display_name="Test PG Tank")
    postgres_db.add(v)
    postgres_db.commit()
    
    saved_v = postgres_db.query(Vehicle).filter(Vehicle.vehicle_id == v_id).first()
    assert saved_v is not None
    assert saved_v.vehicle_class == "TANK"
    
    ir = InferenceRun(
        vehicle_id=v_id,
        vehicle_class="TANK",
        timestep_count=30,
        status="SUCCESS"
    )
    postgres_db.add(ir)
    postgres_db.commit()
    
    # Telemetry
    tr = TelemetryRecord(
        inference_id=ir.id,
        vehicle_id=v_id,
        timestep=0,
        telemetry_json={"temp": 95}
    )
    postgres_db.add(tr)
    
    # Inference
    res = InferenceResult(
        inference_id=ir.id,
        rf_result={"abnormal_detected": False},
        lstm_result=15.5,
        xgb_result=12.2,
        fusion_rul_hours=12.2,
        fusion_method="1.00 × XGBoost"
    )
    postgres_db.add(res)
    
    # Agent
    ar = AgentResult(
        inference_id=ir.id,
        agent_name="monitoring",
        agent_output={"status": "SUCCESS"}
    )
    postgres_db.add(ar)
    
    # Readiness
    fr = FleetReadiness(
        inference_id=ir.id,
        readiness_status="READY",
        ready_count=1,
        attention_count=0,
        not_ready_count=0,
        unknown_count=0
    )
    postgres_db.add(fr)
    
    postgres_db.commit()
    
    # Verify relations
    saved_ir = postgres_db.query(InferenceRun).filter(InferenceRun.id == ir.id).first()
    assert len(saved_ir.telemetry_records) == 1
    assert saved_ir.inference_result.fusion_rul_hours == 12.2
    assert saved_ir.fleet_readiness.readiness_status == "READY"
    assert len(saved_ir.agent_results) == 1

def test_postgres_transaction_rollback(postgres_db):
    """Test that a failing transaction correctly rolls back and doesn't pollute."""
    v_id = f"TEST-PG-{uuid.uuid4().hex[:8]}"
    v = Vehicle(vehicle_id=v_id, vehicle_class="LOGISTIC TRUCK")
    postgres_db.add(v)
    postgres_db.commit()
    
    ir = InferenceRun(
        vehicle_id=v_id,
        vehicle_class="LOGISTIC TRUCK",
        timestep_count=30,
        status="SUCCESS"
    )
    postgres_db.add(ir)
    postgres_db.commit()
    
    initial_count = postgres_db.query(TelemetryRecord).count()
    
    try:
        # Invalid telemetry mapping
        tr = TelemetryRecord(
            inference_id=ir.id,
            vehicle_id=v_id,
            timestep=0,
            # Missing mandatory JSON data to trigger constraint error
        )
        postgres_db.add(tr)
        postgres_db.commit()
        assert False, "Should have thrown IntegrityError"
    except sqlalchemy.exc.IntegrityError:
        postgres_db.rollback()
        
    final_count = postgres_db.query(TelemetryRecord).count()
    assert initial_count == final_count
