from app.simulation import generate_reading_for_field
from app.models import Field

def test_generate_reading(db_session):
    field = Field(name="Test", area_acres=10, crop_type="Corn")
    db_session.add(field)
    db_session.commit()
    
    reading = generate_reading_for_field(db_session, field)
    assert 0 <= reading.soil_moisture <= 100
    assert 0 <= reading.humidity <= 100
    assert reading.rainfall >= 0