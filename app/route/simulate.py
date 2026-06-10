from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.simulation import simulate_all_fields

router = APIRouter(prefix="/api/simulate", tags=["Simulation"])

@router.post("/trigger")
def trigger_simulation(db: Session = Depends(get_db)):
    simulate_all_fields(db)
    return {"message": "✅ Sensor data updated."}