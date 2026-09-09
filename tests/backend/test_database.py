import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base, Vehicle, InferenceRun, TelemetryRecord, InferenceResult, AgentResult, FleetReadiness

@pytest.fixture(scope="module")
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

def test_database_tables_exist(test_db):
    """Test that all required tables are created in the database schema."""
    # We can implicitly test this by performing basic operations
    assert test_db.query(Vehicle).count() == 0
    assert test_db.query(InferenceRun).count() == 0

def test_vehicle_insertion(test_db):
    """Test inserting a vehicle into the database."""
    v = Vehicle(vehicle_id="V-100", vehicle_class="TANK", display_name="TANK V-100")
    test_db.add(v)
    test_db.commit()
    
    saved_v = test_db.query(Vehicle).filter(Vehicle.vehicle_id == "V-100").first()
    assert saved_v is not None
    assert saved_v.vehicle_class == "TANK"

def test_inference_run_insertion(test_db):
    """Test inserting an inference run linked to a vehicle."""
    v = test_db.query(Vehicle).filter(Vehicle.vehicle_id == "V-100").first()
    ir = InferenceRun(vehicle_id=v.vehicle_id, vehicle_class=v.vehicle_class, timestep_count=30, status="READY")
    test_db.add(ir)
    test_db.commit()
    
    saved_ir = test_db.query(InferenceRun).first()
    assert saved_ir is not None
    assert saved_ir.timestep_count == 30
