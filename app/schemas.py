from pydantic import BaseModel, Field
from datetime import datetime

class FieldBase(BaseModel):
    name: str
    area_acres: float = Field(..., ge=0)
    crop_type: str

class FieldCreate(FieldBase):
    pass

class FieldResponse(FieldBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SensorReadingBase(BaseModel):
    soil_moisture: float = Field(..., ge=0, le=100)
    temperature: float = Field(..., ge=-10, le=60)
    humidity: float = Field(..., ge=0, le=100)
    rainfall: float = Field(..., ge=0)

class SensorReadingResponse(SensorReadingBase):
    id: int
    field_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    field_id: int
    field_name: str
    latest_reading: SensorReadingResponse
    status: str
    action: str
    message: str

class TrendPoint(BaseModel):
    timestamp: datetime
    soil_moisture: float