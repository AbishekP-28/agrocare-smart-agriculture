def test_create_field_via_api(client):
    response = client.post("/api/fields/", json={
        "name": "Test Field",
        "area_acres": 5.0,
        "crop_type": "Rice"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Field"
    assert "id" in data

def test_list_fields(client):
    response = client.get("/api/fields/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)