import uuid

from fastapi.testclient import TestClient

from app import main as main_module
from app.external_data import ExternalDataError


client = TestClient(main_module.app)


def register_and_login(username_prefix: str, password: str = "TestPass123"):
    unique_id = uuid.uuid4().hex[:8]
    username = f"{username_prefix}_{unique_id}"
    email = f"{username}@example.com"

    register_response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code in [200, 201], (
        f"Registration failed: {register_response.status_code} - "
        f"{register_response.text}"
    )

    login_response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert login_response.status_code == 200, (
        f"Login failed: {login_response.status_code} - "
        f"{login_response.text}"
    )

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_farm(headers, name="Live Data Test Farm"):
    response = client.post(
        "/farms",
        json={
            "farm_name": name,
            "farm_size_acres": 5.0,
            "state": "Uttarakhand",
            "district": "Nainital",
            "latitude": 29.2183,
            "longitude": 79.5130,
        },
        headers=headers,
    )

    assert response.status_code in [200, 201], (
        f"Farm creation failed: {response.status_code} - "
        f"{response.text}"
    )

    return response.json()["id"]


def sample_live_weather():
    return {
        "provider": "Open-Meteo",
        "latitude": 29.2183,
        "longitude": 79.5130,
        "timezone": "Asia/Kolkata",
        "current": {
            "temperature_2m": 22.5,
            "relative_humidity_2m": 68,
            "precipitation": 1.2,
            "rain": 1.0,
            "wind_speed_10m": 8.5,
            "weather_code": 61,
        },
        "daily": {
            "temperature_2m_max": [29.0],
            "temperature_2m_min": [15.0],
            "precipitation_sum": [8.0],
            "et0_fao_evapotranspiration": [4.2],
        },
    }


def sample_decision():
    return {
        "recommended_crop": {
            "crop": "PIGEONPEA",
            "predicted_yield_kg_per_ha": 1120.47,
        },
        "water_analysis": {
            "water_coverage_percent": 91.84,
        },
        "fertilizer_analysis": {
            "fertilizer_priority": "Moderate",
        },
        "climate_analysis": {
            "climate_risk": 21.15,
        },
        "sustainability": {
            "sustainability_score": 85.46,
        },
        "advisor": {
            "recommended_water_liters": 45000,
        },
    }


def sample_ai_advice():
    return {
        "summary": "Current conditions are manageable for the recommended crop.",
        "recommendation": "Monitor water and nutrient conditions closely.",
        "reasons": ["Water coverage is adequate."],
        "expected_impact": ["Supports stable crop development."],
        "warnings": ["Model outputs are estimates."],
        "next_steps": ["Continue monitoring weather and soil conditions."],
        "language": "English",
    }


def test_live_weather_returns_mocked_provider_data(monkeypatch):
    headers = register_and_login("live_weather")
    farm_id = create_farm(headers)

    expected_weather = sample_live_weather()
    calls = []

    def fake_get_live_weather(latitude, longitude):
        calls.append((latitude, longitude))
        return expected_weather

    monkeypatch.setattr(main_module, "get_live_weather", fake_get_live_weather)

    response = client.get(
        f"/farms/{farm_id}/weather/live",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == expected_weather
    assert calls == [(29.2183, 79.5130)]


def test_live_weather_returns_503_when_provider_fails(monkeypatch):
    headers = register_and_login("live_weather_error")
    farm_id = create_farm(headers)

    def fake_get_live_weather(latitude, longitude):
        raise ExternalDataError("provider unavailable")

    monkeypatch.setattr(main_module, "get_live_weather", fake_get_live_weather)

    response = client.get(
        f"/farms/{farm_id}/weather/live",
        headers=headers,
    )

    assert response.status_code == 503
    assert "Live weather service unavailable" in response.json()["detail"]


def test_live_soil_returns_mocked_provider_data(monkeypatch):
    headers = register_and_login("live_soil")
    farm_id = create_farm(headers)

    expected_soil = {
        "provider": "SoilGrids",
        "latitude": 29.2183,
        "longitude": 79.5130,
        "properties": {
            "phh2o": {"mean": 68.0},
            "nitrogen": {"mean": 1.8},
            "soc": {"mean": 12.0},
            "clay": {"mean": 220.0},
        },
    }

    def fake_get_soil_data(latitude, longitude):
        return expected_soil

    monkeypatch.setattr(main_module, "get_soil_data", fake_get_soil_data)

    response = client.get(
        f"/farms/{farm_id}/soil/live",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == expected_soil


def test_live_decision_pipeline_uses_live_weather(monkeypatch):
    headers = register_and_login("live_decision")
    farm_id = create_farm(headers)

    expected_weather = sample_live_weather()
    expected_decision = sample_decision()
    pipeline_calls = []

    monkeypatch.setattr(
        main_module,
        "get_live_weather",
        lambda latitude, longitude: expected_weather,
    )

    def fake_run_decision_pipeline(**kwargs):
        pipeline_calls.append(kwargs)
        return expected_decision

    monkeypatch.setattr(
        main_module,
        "run_decision_pipeline",
        fake_run_decision_pipeline,
    )

    payload = {
        "district_code": 800,
        "state_code": 13,
        "year": 2026,
        "district": "Nainital",
        "state_name": "Uttarakhand",
        "area_1000_ha": 24.0,
        "farm_size_acres": 5.0,
        "previous_crop": "RICE",
        "nitrogen": 80,
        "phosphorus": 40,
        "potassium": 30,
        "ph": 6.8,
        "organic_matter": 1.8,
        "available_water_liters": 45000,
        "irrigation_type": "Drip",
        "rainfall_mm": 620,
        "avg_temp_c": 21.5,
        "max_temp_c": 29.0,
        "min_temp_c": 14.0,
    }

    response = client.post(
        f"/farms/{farm_id}/decision-pipeline/live",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()
    assert body["decision"] == expected_decision
    assert body["used_for_pipeline"] == {
        "rainfall_mm": 8.0,
        "avg_temp_c": 22.5,
        "max_temp_c": 29.0,
        "min_temp_c": 15.0,
    }

    assert len(pipeline_calls) == 1
    assert pipeline_calls[0]["rainfall_mm"] == 8.0
    assert pipeline_calls[0]["avg_temp_c"] == 22.5
    assert pipeline_calls[0]["max_temp_c"] == 29.0
    assert pipeline_calls[0]["min_temp_c"] == 15.0


def test_ai_advisor_returns_mocked_structured_advice(monkeypatch):
    expected_advice = sample_ai_advice()
    calls = []

    def fake_generate_ai_advice(**kwargs):
        calls.append(kwargs)
        return expected_advice

    monkeypatch.setattr(
        main_module,
        "generate_ai_advice",
        fake_generate_ai_advice,
    )

    payload = {
        "crop": "PIGEONPEA",
        "predicted_yield_kg_per_ha": 1120.47,
        "water_coverage_percent": 91.84,
        "fertilizer_priority": "Moderate",
        "sustainability_score": 85.46,
        "climate_risk": 21.15,
        "recommended_water_liters": 45000,
        "rainfall_mm": 8.0,
        "avg_temp_c": 22.5,
        "max_temp_c": 29.0,
        "min_temp_c": 15.0,
        "soil_ph": 6.8,
        "organic_matter": 1.8,
        "language": "English",
    }

    response = client.post(
        "/agricultural-advisor/ai",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json() == expected_advice
    assert calls[0]["crop"] == "PIGEONPEA"
    assert calls[0]["predicted_yield_kg_per_ha"] == 1120.47
    assert calls[0]["language"] == "English"


def test_ai_advisor_returns_503_when_provider_fails(monkeypatch):
    def fake_generate_ai_advice(**kwargs):
        raise RuntimeError("GEMINI_API_KEY is not configured")

    monkeypatch.setattr(
        main_module,
        "generate_ai_advice",
        fake_generate_ai_advice,
    )

    response = client.post(
        "/agricultural-advisor/ai",
        json={
            "crop": "WHEAT",
            "predicted_yield_kg_per_ha": 3200,
            "water_coverage_percent": 78,
            "fertilizer_priority": "Moderate",
            "sustainability_score": 72,
            "climate_risk": 28,
        },
    )

    assert response.status_code == 503
    assert "GEMINI_API_KEY is not configured" in response.json()["detail"]


def test_live_ai_pipeline_connects_weather_decision_and_ai(monkeypatch):
    headers = register_and_login("live_ai_pipeline")
    farm_id = create_farm(headers)

    expected_weather = sample_live_weather()
    expected_decision = sample_decision()
    expected_advice = sample_ai_advice()
    ai_calls = []

    monkeypatch.setattr(
        main_module,
        "get_live_weather",
        lambda latitude, longitude: expected_weather,
    )
    monkeypatch.setattr(
        main_module,
        "run_decision_pipeline",
        lambda **kwargs: expected_decision,
    )

    def fake_generate_ai_advice(**kwargs):
        ai_calls.append(kwargs)
        return expected_advice

    monkeypatch.setattr(
        main_module,
        "generate_ai_advice",
        fake_generate_ai_advice,
    )

    payload = {
        "district_code": 800,
        "state_code": 13,
        "year": 2026,
        "district": "Nainital",
        "state_name": "Uttarakhand",
        "area_1000_ha": 24.0,
        "farm_size_acres": 5.0,
        "previous_crop": "RICE",
        "nitrogen": 80,
        "phosphorus": 40,
        "potassium": 30,
        "ph": 6.8,
        "organic_matter": 1.8,
        "available_water_liters": 45000,
        "irrigation_type": "Drip",
        "rainfall_mm": 620,
        "avg_temp_c": 21.5,
        "max_temp_c": 29.0,
        "min_temp_c": 14.0,
        "language": "English",
    }

    response = client.post(
        f"/farms/{farm_id}/decision-pipeline/ai",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()
    assert body["live_weather"] == expected_weather
    assert body["decision"] == expected_decision
    assert body["ai_advice"] == expected_advice
    assert body["used_for_pipeline"] == {
        "rainfall_mm": 8.0,
        "avg_temp_c": 22.5,
        "max_temp_c": 29.0,
        "min_temp_c": 15.0,
    }

    assert len(ai_calls) == 1
    assert ai_calls[0]["crop"] == "PIGEONPEA"
    assert ai_calls[0]["predicted_yield_kg_per_ha"] == 1120.47
    assert ai_calls[0]["water_coverage_percent"] == 91.84
    assert ai_calls[0]["fertilizer_priority"] == "Moderate"
    assert ai_calls[0]["sustainability_score"] == 85.46
    assert ai_calls[0]["climate_risk"] == 21.15
    assert ai_calls[0]["recommended_water_liters"] == 45000
    assert ai_calls[0]["soil_ph"] == 6.8
    assert ai_calls[0]["organic_matter"] == 1.8
