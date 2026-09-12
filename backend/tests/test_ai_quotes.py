from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.ai import ParsedQuoteRequest


client = TestClient(app)


def get_sales_token():
    response = client.post(
        "/api/auth/login",
        json={
            "username": "sales",
            "password": "Sales123!",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_ai_quote(
    mock_parse_quote_request,
):
    mock_parse_quote_request.return_value = (
        ParsedQuoteRequest(
            customer_name="Pacific Mountain Outfitters",
            product_name="Alpine Shell Jacket",
            quantity=30,
        )
    )

    token = get_sales_token()

    response = client.post(
        "/api/ai/quote",
        json={
            "message": (
                "Can Pacific Mountain Outfitters "
                "get 30 Alpine Shell Jackets?"
            )
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["customer_code"] == "BP-20001"
    assert data["sku"] == "JACKET-BETA-AR-M"
    assert data["quantity_requested"] == 30
    assert data["fulfillment_status"] == "available"


@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_ai_quote_missing_quantity(
    mock_parse_quote_request,
):
    mock_parse_quote_request.return_value = (
        ParsedQuoteRequest(
            customer_name="Pacific Mountain Outfitters",
            product_name="Alpine Shell Jacket",
            quantity=None,
        )
    )

    token = get_sales_token()

    response = client.post(
        "/api/ai/quote",
        json={
            "message": (
                "Pacific Mountain Outfitters "
                "needs Alpine Shell Jackets."
            )
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 422


@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_ai_quote_large_order(
    mock_parse_quote_request,
):
    mock_parse_quote_request.return_value = (
        ParsedQuoteRequest(
            customer_name="Pacific Mountain Outfitters",
            product_name="Alpine Shell Jacket",
            quantity=500,
        )
    )

    token = get_sales_token()

    response = client.post(
        "/api/ai/quote",
        json={
            "message": (
                "Pacific Mountain Outfitters "
                "wants 500 Alpine Shell Jackets."
            )
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["fulfillment_status"] == "partial"
    assert data["requires_approval"] is True

    assert (
        "Requested quantity cannot be fully fulfilled"
        in data["approval_reasons"]
    )


def test_ai_quote_requires_authentication():
    response = client.post(
        "/api/ai/quote",
        json={
            "message": (
                "Pacific Mountain Outfitters "
                "wants 1 Merino Wool Toque."
            )
        },
    )

    assert response.status_code in (401, 403)