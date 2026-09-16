from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.ai import ParsedQuoteRequest


client = TestClient(app)


def get_token(
    username: str,
    password: str,
) -> str:
    response = client.post(
        "/api/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()[
        "access_token"
    ]


def quote_headers(
    token: str,
    key: str | None = None,
) -> dict:
    headers = {
        "Authorization":
            f"Bearer {token}"
    }

    if key:
        headers["Idempotency-Key"] = key

    return headers


@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_duplicate_quote_returns_cached_response(
    mock_parse,
):
    mock_parse.return_value = (
        ParsedQuoteRequest(
            customer_name=(
                "Pacific Mountain Outfitters"
            ),
            product_name="Merino Wool Toque",
            quantity=1,
        )
    )

    token = get_token(
        "sales",
        "Sales123!",
    )

    key = str(
        uuid4()
    )

    body = {
        "message": (
            "Pacific Mountain Outfitters "
            "wants 1 Merino Wool Toque."
        )
    }

    headers = quote_headers(
        token,
        key,
    )

    first = client.post(
        "/api/ai/quote",
        json=body,
        headers=headers,
    )

    second = client.post(
        "/api/ai/quote",
        json=body,
        headers=headers,
    )

    assert first.status_code == 200
    assert second.status_code == 200

    assert (
        first.json()["thread_id"]
        == second.json()["thread_id"]
    )

    assert mock_parse.call_count == 1


@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_same_key_different_request_returns_409(
    mock_parse,
):
    mock_parse.return_value = (
        ParsedQuoteRequest(
            customer_name=(
                "Pacific Mountain Outfitters"
            ),
            product_name="Merino Wool Toque",
            quantity=1,
        )
    )

    token = get_token(
        "sales",
        "Sales123!",
    )

    key = str(
        uuid4()
    )

    headers = quote_headers(
        token,
        key,
    )

    first = client.post(
        "/api/ai/quote",
        json={
            "message": "First request"
        },
        headers=headers,
    )

    assert first.status_code == 200

    second = client.post(
        "/api/ai/quote",
        json={
            "message": "Different request"
        },
        headers=headers,
    )

    assert second.status_code == 409


def test_quote_requires_idempotency_key():
    token = get_token(
        "sales",
        "Sales123!",
    )

    response = client.post(
        "/api/ai/quote",
        json={
            "message": "Create quote"
        },
        headers={
            "Authorization":
                f"Bearer {token}"
        },
    )

    assert response.status_code == 422


def test_short_idempotency_key_is_rejected():
    token = get_token(
        "sales",
        "Sales123!",
    )

    response = client.post(
        "/api/ai/quote",
        json={
            "message": "Create quote"
        },
        headers={
            "Authorization":
                f"Bearer {token}",
            "Idempotency-Key": "abc",
        },
    )

    assert response.status_code == 422