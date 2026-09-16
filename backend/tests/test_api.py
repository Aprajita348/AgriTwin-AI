from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200


def test_docs():
    response = client.get("/docs")

    assert response.status_code == 200


def test_predict_yield():
    payload = {
        "district_code": 63,
        "state_code": 20,
        "year": 2026,
        "crop": "MAIZE",
        "district": "Adilabad",
        "state_name": "Telangana",
        "area_1000_ha": 30.5,
        "rainfall_mm": 1106.23,
        "avg_temp_c": 27.4,
        "max_temp_c": 33.47,
        "min_temp_c": 21.33,
    }

    response = client.post("/predict-yield", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "predicted_yield_kg_per_ha" in data
    assert data["predicted_yield_kg_per_ha"] >= 0


def test_crop_calendar():
    response = client.post(
        "/crop-calendar",
        json={"crop": "WHEAT"},
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)


def test_decision_pipeline():
    payload = {
        "district_code": 63,
        "state_code": 20,
        "year": 2026,
        "district": "Adilabad",
        "state_name": "Telangana",
        "area_1000_ha": 30.5,
        "farm_size_acres": 5,
        "previous_crop": "MAIZE",
        "nitrogen": 240,
        "phosphorus": 45,
        "potassium": 180,
        "ph": 6.8,
        "organic_matter": 3.2,
        "available_water_liters": 50000,
        "irrigation_type": "Drip",
        "rainfall_mm": 1106.23,
        "avg_temp_c": 27.4,
        "max_temp_c": 33.47,
        "min_temp_c": 21.33,
    }

    response = client.post("/decision-pipeline", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "recommended_crop" in data
    assert "sustainability" in data

    recommended_crop = data["recommended_crop"]

    assert "crop" in recommended_crop
    assert "predicted_yield_kg_per_ha" in recommended_crop
    assert recommended_crop["predicted_yield_kg_per_ha"] >= 0