from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_customer():
    response = client.get(
        "/api/customers/BP-20001"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["customer_code"] == "BP-20001"
    assert data["name"] == "Pacific Mountain Outfitters"
    assert data["region"] == "BC"
    assert data["pricing_tier"] == "B"


def test_search_customer():
    response = client.get(
        "/api/customers/?name=Pacific"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0
    assert data[0]["name"] == "Pacific Mountain Outfitters"


def test_customer_not_found():
    response = client.get(
        "/api/customers/BP-99999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Customer not found"