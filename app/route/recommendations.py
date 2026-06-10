from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, recommendation
from app.database import get_db

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

@router.get("/fields/{field_id}", response_model=schemas.RecommendationResponse)
def get_recommendation(field_id: int, db: Session = Depends(get_db)):
    field = db.query(models.Field).filter(models.Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    latest, status, action, msg, extra = recommendation.get_recommendation_for_field(db, field)
    if not latest:
        raise HTTPException(status_code=404, detail="No sensor data yet for this field")
    return schemas.RecommendationResponse(
        field_id=field.id,
        field_name=field.name,
        latest_reading=latest,
        status=status,
        action=action,
        message=msg
    )