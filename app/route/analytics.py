from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/field-trend/{field_id}", response_model=list[schemas.TrendPoint])
def field_trend(field_id: int, days: int = 7, db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    field = db.query(models.Field).filter(models.Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    since = datetime.utcnow() - timedelta(days=days)
    readings = db.query(models.SensorReading).filter(
        models.SensorReading.field_id == field_id,
        models.SensorReading.timestamp >= since
    ).order_by(models.SensorReading.timestamp.asc()).all()
    return [schemas.TrendPoint(
        timestamp=r.timestamp,
        soil_moisture=r.soil_moisture
    ) for r in readings]