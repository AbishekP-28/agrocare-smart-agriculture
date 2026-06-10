import random
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Field, SensorReading

def get_last_reading(db: Session, field_id: int):
    return db.query(SensorReading).filter(
        SensorReading.field_id == field_id
    ).order_by(SensorReading.timestamp.desc()).first()

def generate_reading_for_field(db: Session, field: Field) -> SensorReading:
    last = get_last_reading(db, field.id)
    
    if last:
        soil_moisture = last.soil_moisture
        temperature = last.temperature
        humidity = last.humidity
        rainfall = last.rainfall
    else:
        soil_moisture = random.uniform(40, 60)
        temperature = random.uniform(20, 30)
        humidity = random.uniform(40, 70)
        rainfall = 0.0
    
    # Evaporation
    evap = random.uniform(0, 10)
    soil_moisture -= evap
    
    # Temperature variation
    temperature += random.uniform(-2, 2)
    temperature = max(10, min(45, temperature))
    
    # Humidity variation
    humidity += random.uniform(-8, 8)
    humidity = max(20, min(90, humidity))
    
    # Random rainfall (20% chance)
    rainfall = 0.0
    if random.random() < 0.4:
        rainfall = random.uniform(1, 15)
        soil_moisture += rainfall * 0.8
    
    soil_moisture = max(0, min(100, soil_moisture))

    if soil_moisture < 19:
        soil_moisture = random.uniform(20, 60)
    
    new_reading = SensorReading(
        field_id=field.id,
        soil_moisture=round(soil_moisture, 1),
        temperature=round(temperature, 1),
        humidity=round(humidity, 1),
        rainfall=round(rainfall, 1),
        timestamp=datetime.utcnow()
    )
    return new_reading

def simulate_all_fields(db: Session):
    fields = db.query(Field).all()
    new_readings = []
    for field in fields:
        reading = generate_reading_for_field(db, field)
        db.add(reading)
        new_readings.append(reading)
    db.commit()
    return new_readings