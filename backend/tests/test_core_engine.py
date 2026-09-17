from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)



def test_water_optimization_returns_core_metrics():
    response = client.post(
        "/optimize-water",
        json={
            "farm_size_acres": 5.0,
            "crop": "WHEAT",
            "rainfall_mm": 620,
            "avg_temp_c": 21.5,
            "available_water_liters": 45000,
            "irrigation_type": "Drip",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)

    # Verify fields that the current water optimizer actually returns.
    assert "crop" in data
    assert "farm_size_hectares" in data
    assert "crop_coefficient" in data
    assert "base_et_mm" in data

    assert isinstance(data["crop"], str)
    assert data["farm_size_hectares"] > 0
    assert data["crop_coefficient"] > 0
    assert data["base_et_mm"] >= 0

def test_fertilizer_optimization_returns_priority_analysis():
    response = client.post(
        "/optimize-fertilizer",
        json={
            "farm_size_acres": 5.0,
            "crop": "WHEAT",
            "nitrogen": 80,
            "phosphorus": 40,
            "potassium": 30,
            "ph": 6.8,
            "organic_matter": 1.8,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "priority_nutrient" in data
    assert "fertilizer_priority" in data
    assert isinstance(data["priority_nutrient"], str)
    assert isinstance(data["fertilizer_priority"], str)


def test_early_warning_returns_warning_analysis():
    response = client.post(
        "/early-warning",
        json={
            "crop": "WHEAT",
            "avg_temp_c": 21.5,
            "rainfall_mm": 620,
            "available_water_liters": 45000,
            "farm_size_acres": 5.0,
            "nitrogen": 80,
            "phosphorus": 40,
            "potassium": 30,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, (dict, list))

    if isinstance(data, dict):
        assert any(
            key in data
            for key in ("warnings", "early_warnings", "risk_level", "summary")
        )


def test_what_if_returns_scenario_comparison():
    response = client.post(
        "/what-if",
        json={
            "crop": "WHEAT",
            "farm_size_acres": 5.0,
            "baseline_yield_kg_per_ha": 3200,
            "baseline_profit": 80000,
            "baseline_water_liters": 45000,
            "baseline_sustainability_score": 72,
            "avg_temp_c": 21.5,
            "rainfall_mm": 620,
            "temperature_change": 2.0,
            "rainfall_change_percent": -10.0,
            "irrigation_change_percent": 5.0,
            "fertilizer_change_percent": -10.0,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    assert any(
        key in data
        for key in ("baseline", "scenario", "comparison", "yield_change", "profit_change")
    )


def test_decision_replay_returns_replay_metrics():
    response = client.post(
        "/decision-replay",
        json={
            "recommendation_id": 1,
            "decision_taken": "IMPLEMENTED",
            "predicted_yield": 3200,
            "actual_yield": 3100,
            "predicted_water": 45000,
            "actual_water": 47000,
            "predicted_profit": 80000,
            "actual_profit": 76000,
            "notes": "Test replay",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["recommendation_id"] == 1
    assert data["decision_taken"] == "IMPLEMENTED"
    assert len(data) > 2
