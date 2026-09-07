from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_product_inventory():
    response = client.get(
        "/api/inventory/JACKET-BETA-AR-M"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sku"] == "JACKET-BETA-AR-M"
    assert data["product_name"] == "Alpine Shell Jacket"

    assert data["total_available"] == 105
    assert len(data["warehouses"]) == 3


def test_get_warehouse_inventory():
    response = client.get(
        "/api/inventory/JACKET-BETA-AR-M/VAN"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["warehouse_code"] == "VAN"
    assert data["quantity_available"] == 42
    assert data["quantity_reserved"] == 7


def test_warehouse_not_found():
    response = client.get(
        "/api/inventory/JACKET-BETA-AR-M/XYZ"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Warehouse not found"


def test_inventory_product_not_found():
    response = client.get(
        "/api/inventory/INVALID-SKU"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Product not found"