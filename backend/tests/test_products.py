from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_product():
    response = client.get(
        "/api/products/JACKET-BETA-AR-M"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sku"] == "JACKET-BETA-AR-M"
    assert data["name"] == "Alpine Shell Jacket"
    assert data["category"] == "Jackets"


def test_search_products():
    response = client.get(
        "/api/products/?search=jacket"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1


def test_product_not_found():
    response = client.get(
        "/api/products/INVALID-SKU"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Product not found"