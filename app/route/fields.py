from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/fields", tags=["Fields"])


@router.get("/", response_model=list[schemas.FieldResponse])
def list_fields(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return db.query(models.Field).filter(models.Field.user_id == user_id).all()


@router.get("/{field_id}", response_model=schemas.FieldResponse)
def get_field(request: Request, field_id: int, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    field = db.query(models.Field).filter(
        models.Field.id == field_id,
        models.Field.user_id == user_id
    ).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field