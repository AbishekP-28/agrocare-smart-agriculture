def test_field_trend(client):
    # Create field first
    field_resp = client.post("/api/fields/", json={
        "name": "Trend Field",
        "area_acres": 3,
        "crop_type": "Wheat"
    })
    field_id = field_resp.json()["id"]
    
    # Trigger simulation
    client.post("/api/simulate/trigger")
    
    # Get trend
    response = client.get(f"/api/analytics/field-trend/{field_id}?days=1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)