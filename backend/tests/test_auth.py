from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_login_success():
    response = client.post(
        "/api/auth/login",
        json={
            "username": "sales",
            "password": "Sales123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data

    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    response = client.post(
        "/api/auth/login",
        json={
            "username": "sales",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401

def get_sales_token():
    response = client.post(
        "/api/auth/login",
        json={
            "username": "sales",
            "password": "Sales123!",
        },
    )

    return response.json()[
        "access_token"
    ]

def test_get_current_user():
    token = get_sales_token()

    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization":
                f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "sales"
    assert data["role"] == "sales_rep"

def test_invalid_token():
    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization":
                "Bearer invalid-token"
        },
    )

    assert response.status_code == 401