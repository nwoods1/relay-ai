from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_available_quote():
    response = client.post(
        "/api/quotes/",
        json={
            "customer_code": "BP-20001",
            "sku": "JACKET-BETA-AR-M",
            "quantity": 30,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["customer_code"] == "BP-20001"
    assert data["sku"] == "JACKET-BETA-AR-M"
    assert data["quantity_requested"] == 30
    assert data["fulfillment_status"] == "available"


def test_create_partial_quote():
    response = client.post(
        "/api/quotes/",
        json={
            "customer_code": "BP-20001",
            "sku": "JACKET-BETA-AR-M",
            "quantity": 500,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["fulfillment_status"] == "partial"
    assert data["requires_approval"] is True


def test_quote_customer_not_found():
    response = client.post(
        "/api/quotes/",
        json={
            "customer_code": "BP-99999",
            "sku": "JACKET-BETA-AR-M",
            "quantity": 30,
        },
    )

    assert response.status_code == 404


def test_quote_product_not_found():
    response = client.post(
        "/api/quotes/",
        json={
            "customer_code": "BP-20001",
            "sku": "BAD-SKU",
            "quantity": 30,
        },
    )

    assert response.status_code == 404


def test_quote_rejects_zero_quantity():
    response = client.post(
        "/api/quotes/",
        json={
            "customer_code": "BP-20001",
            "sku": "JACKET-BETA-AR-M",
            "quantity": 0,
        },
    )

    assert response.status_code == 422

def test_quote_uses_customer_pricing_tier():
    response = client.post(
        "/api/quotes/",
        json={
            "customer_code": "BP-20002",
            "sku": "JACKET-BETA-AR-M",
            "quantity": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["pricing_tier"] == "A"
    assert float(data["unit_price"]) == 679.99

def test_quote_allocates_multiple_warehouses():
    response = client.post(
        "/api/quotes/",
        json={
            "customer_code": "BP-20001",
            "sku": "JACKET-BETA-AR-M",
            "quantity": 50,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["warehouse_allocations"]) == 2

    assert data["warehouse_allocations"][0]["warehouse_code"] == "VAN"
    assert data["warehouse_allocations"][0]["quantity"] == 35

    assert data["warehouse_allocations"][1]["warehouse_code"] == "CAL"
    assert data["warehouse_allocations"][1]["quantity"] == 15