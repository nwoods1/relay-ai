from unittest.mock import patch
from uuid import uuid4

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


def get_headers(
    token: str,
) -> dict:
    return {
        "Authorization":
            f"Bearer {token}",
        "Idempotency-Key":
            str(uuid4()),
    }


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
            quantity=20,
        )
    )

    token = get_sales_token()

    response = client.post(
        "/api/ai/quote",
        json={
            "message": (
                "Can Pacific Mountain Outfitters "
                "get 20 Alpine Shell Jackets?"
            )
        },
        headers=get_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert data["thread_id"]
    assert data["approval_request"] is None

    assert (
        data["quote"]["customer_code"]
        == "BP-20001"
    )

    assert (
        data["quote"]["sku"]
        == "JACKET-BETA-AR-M"
    )

    assert (
        data["quote"]["quantity_requested"]
        == 20
    )

    assert (
        data["quote"]["fulfillment_status"]
        == "available"
    )

    assert (
        data["quote"]["requires_approval"]
        is False
    )


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
        headers=get_headers(token),
    )

    assert response.status_code in (
        200,
        422,
    )

    if response.status_code == 200:
        assert (
            response.json()["status"]
            == "failed"
        )


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
        headers=get_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["status"]
        == "awaiting_approval"
    )

    assert data["thread_id"]
    assert data["approval_request"]

    assert (
        data["quote"]["fulfillment_status"]
        == "partial"
    )

    assert (
        data["quote"]["requires_approval"]
        is True
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
        headers={
            "Idempotency-Key":
                str(uuid4())
        },
    )

    assert response.status_code in (
        401,
        403,
    )