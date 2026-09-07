from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_customer_pricing():
    response = client.get(
        "/api/pricing/BP-20001/JACKET-BETA-AR-M"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["customer_code"] == "BP-20001"
    assert data["sku"] == "JACKET-BETA-AR-M"
    assert data["pricing_tier"] == "B"
    assert float(data["unit_price"]) == 714.99


def test_tier_a_customer_gets_lower_price():
    response = client.get(
        "/api/pricing/BP-20002/JACKET-BETA-AR-M"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["pricing_tier"] == "A"
    assert float(data["unit_price"]) == 679.99


def test_pricing_customer_not_found():
    response = client.get(
        "/api/pricing/BP-99999/JACKET-BETA-AR-M"
    )

    assert response.status_code == 404


def test_pricing_product_not_found():
    response = client.get(
        "/api/pricing/BP-20001/INVALID-SKU"
    )

    assert response.status_code == 404