from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.ai import ParsedQuoteRequest


client = TestClient(app)


@patch(
    "app.services.ai_quote_service.parse_quote_request"
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

    response = client.post(
        "/api/ai/quote",
        json={
            "message": (
                "Can Pacific Mountain Outfitters "
                "get 30 Alpine Shell Jackets?"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["customer_code"] == "BP-20001"
    assert data["sku"] == "JACKET-BETA-AR-M"

@patch(
    "app.services.ai_quote_service.parse_quote_request"
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

    response = client.post(
        "/api/ai/quote",
        json={
            "message": (
                "Pacific Mountain Outfitters "
                "needs Alpine Shell Jackets."
            )
        },
    )

    assert response.status_code == 422