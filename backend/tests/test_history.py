import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def register_and_login(username_prefix, password="TestPass123"):
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
        f"Registration failed: "
        f"{register_response.status_code} - "
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
        f"Login failed: "
        f"{login_response.status_code} - "
        f"{login_response.text}"
    )

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def create_farm(headers, name="Test Farm"):
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
        f"Farm creation failed: "
        f"{response.status_code} - "
        f"{response.text}"
    )

    return response.json()["id"]


def test_prediction_history_requires_auth():
    response = client.get(
        "/farms/999999/predictions"
    )

    assert response.status_code == 401


def test_simulation_history_requires_auth():
    response = client.get(
        "/farms/999999/simulations"
    )

    assert response.status_code == 401


def test_recommendation_history_requires_auth():
    response = client.get(
        "/farms/999999/recommendations"
    )

    assert response.status_code == 401


def test_feedback_history_requires_auth():
    response = client.get(
        "/farms/999999/feedback"
    )

    assert response.status_code == 401


def test_cross_user_history_access_is_blocked():
    user1_headers = register_and_login(
        "historyuser1"
    )

    user2_headers = register_and_login(
        "historyuser2"
    )

    farm_id = create_farm(
        user1_headers,
        "User 1 Farm"
    )

    response = client.get(
        f"/farms/{farm_id}/predictions",
        headers=user2_headers,
    )

    assert response.status_code == 404


def test_cross_user_simulation_access_is_blocked():
    user1_headers = register_and_login(
        "simulationuser1"
    )

    user2_headers = register_and_login(
        "simulationuser2"
    )

    farm_id = create_farm(
        user1_headers,
        "Simulation Farm"
    )

    response = client.get(
        f"/farms/{farm_id}/simulations",
        headers=user2_headers,
    )

    assert response.status_code == 404


def test_cross_user_recommendation_access_is_blocked():
    user1_headers = register_and_login(
        "recommendationuser1"
    )

    user2_headers = register_and_login(
        "recommendationuser2"
    )

    farm_id = create_farm(
        user1_headers,
        "Recommendation Farm"
    )

    response = client.get(
        f"/farms/{farm_id}/recommendations",
        headers=user2_headers,
    )

    assert response.status_code == 404


def test_cross_user_feedback_access_is_blocked():
    user1_headers = register_and_login(
        "feedbackuser1"
    )

    user2_headers = register_and_login(
        "feedbackuser2"
    )

    farm_id = create_farm(
        user1_headers,
        "Feedback Farm"
    )

    response = client.get(
        f"/farms/{farm_id}/feedback",
        headers=user2_headers,
    )

    assert response.status_code == 404