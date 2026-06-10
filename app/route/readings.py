from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/readings", tags=["Readings"])

@router.get("/fields/{field_id}", response_model=list[schemas.SensorReadingResponse])
def get_field_readings(
    field_id: int,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    field = db.query(models.Field).filter(models.Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    readings = db.query(models.SensorReading).filter(
        models.SensorReading.field_id == field_id
    ).order_by(models.SensorReading.timestamp.desc()).limit(limit).all()
    return readings