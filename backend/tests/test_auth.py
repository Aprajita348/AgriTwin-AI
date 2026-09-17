from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_test_user(
    username: str,
    email: str,
    password: str,
):
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )

    # User may already exist from an earlier local test.
    if response.status_code not in (201, 409):
        raise AssertionError(response.text)


def login_user(
    username: str,
    password: str,
) -> str:
    response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_farms_requires_authentication():
    response = client.get("/farms")

    assert response.status_code == 401


def test_authenticated_user_can_create_and_read_own_farm():
    username = "farmuser01"
    email = "farmuser01@example.com"
    password = "TestPass123!"

    create_test_user(
        username,
        email,
        password,
    )

    token = login_user(
        username,
        password,
    )

    headers = {
        "Authorization": f"Bearer {token}"
    }

    create_response = client.post(
        "/farms",
        headers=headers,
        json={
            "farm_name": "Test Farm One",
            "farm_size_acres": 5,
            "state": "Uttarakhand",
            "district": "Nainital",
            "latitude": 29.39,
            "longitude": 79.45,
        },
    )

    assert create_response.status_code == 201

    farm = create_response.json()

    assert farm["farm_name"] == "Test Farm One"
    assert farm["farm_size_acres"] == 5

    farm_id = farm["id"]

    get_response = client.get(
        f"/farms/{farm_id}",
        headers=headers,
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == farm_id


def test_user_cannot_access_another_users_farm():
    user1_username = "owneruser01"
    user1_email = "owneruser01@example.com"
    user1_password = "TestPass123!"

    user2_username = "otheruser01"
    user2_email = "otheruser01@example.com"
    user2_password = "TestPass123!"

    create_test_user(
        user1_username,
        user1_email,
        user1_password,
    )

    create_test_user(
        user2_username,
        user2_email,
        user2_password,
    )

    token1 = login_user(
        user1_username,
        user1_password,
    )

    token2 = login_user(
        user2_username,
        user2_password,
    )

    headers1 = {
        "Authorization": f"Bearer {token1}"
    }

    headers2 = {
        "Authorization": f"Bearer {token2}"
    }

    create_response = client.post(
        "/farms",
        headers=headers1,
        json={
            "farm_name": "Private Farm",
            "farm_size_acres": 3,
            "state": "Uttarakhand",
            "district": "Nainital",
            "latitude": 29.39,
            "longitude": 79.45,
        },
    )

    assert create_response.status_code == 201

    farm_id = create_response.json()["id"]

    other_user_response = client.get(
        f"/farms/{farm_id}",
        headers=headers2,
    )

    assert other_user_response.status_code == 404


def test_authenticated_user_can_list_only_own_farms():
    username = "listuser01"
    email = "listuser01@example.com"
    password = "TestPass123!"

    create_test_user(
        username,
        email,
        password,
    )

    token = login_user(
        username,
        password,
    )

    headers = {
        "Authorization": f"Bearer {token}"
    }

    create_response = client.post(
        "/farms",
        headers=headers,
        json={
            "farm_name": "List Farm",
            "farm_size_acres": 2,
            "state": "Uttarakhand",
            "district": "Nainital",
            "latitude": 29.39,
            "longitude": 79.45,
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        "/farms",
        headers=headers,
    )

    assert response.status_code == 200

    farms = response.json()

    assert isinstance(farms, list)

    assert all(
        farm["farm_name"] == "List Farm"
        for farm in farms
    )


def test_auth_me_requires_token():
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_auth_me_rejects_invalid_token():
    headers = {
        "Authorization": "Bearer invalid-token"
    }

    response = client.get(
        "/auth/me",
        headers=headers,
    )

    assert response.status_code == 401