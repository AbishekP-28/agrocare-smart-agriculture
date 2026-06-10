from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import Field, SensorReading

def get_recent_rainfall(db: Session, field_id: int, hours=24) -> float:
    since = datetime.utcnow() - timedelta(hours=hours)
    readings = db.query(SensorReading).filter(
        SensorReading.field_id == field_id,
        SensorReading.timestamp >= since
    ).all()
    return readings[-1].rainfall

def get_recommendation_for_field(db: Session, field: Field):
    latest = db.query(SensorReading).filter(
        SensorReading.field_id == field.id
    ).order_by(SensorReading.timestamp.desc()).first()
    
    if not latest:
        return None, None, None, None, None
    
    recent_rain = get_recent_rainfall(db, field.id, 24)
    moisture = latest.soil_moisture
    
    if recent_rain > 5:
        return (
            latest,
            "🟢 Enough Water Available",
            "Wait Due To Recent Rainfall",
            f"Recent rainfall of {recent_rain}mm means no irrigation needed right now.",
            "rain_override"
        )
    
    if moisture < 20:
        return (
            latest,
            "🔴 Water Needed Now",
            "Irrigate Today Evening",
            f"Soil moisture is {moisture}%. Crop needs water immediately.",
            "critical"
        )
    elif moisture < 40:
        return (
            latest,
            "🟡 Water Needed Soon",
            "Irrigate Tomorrow Morning",
            f"Soil moisture is {moisture}%. Plan to irrigate within 24 hours.",
            "dry"
        )
    elif moisture <= 70:
        return (
            latest,
            "🟢 Water Level Good",
            "No Irrigation Needed",
            f"Soil moisture is {moisture}% - optimal range.",
            "good"
        )
    else:
        return (
            latest,
            "🟢 Enough Water Available",
            "Do Not Irrigate",
            f"Soil moisture is {moisture}% - too much water. Let soil dry naturally.",
            "excessive"
        )