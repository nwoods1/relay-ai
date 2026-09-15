from unittest.mock import patch

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

@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_large_quote_waits_for_approval(
    mock_parse_quote_request,
):

    mock_parse_quote_request.return_value = (
        ParsedQuoteRequest(
            customer_name=(
                "Pacific Mountain Outfitters"
            ),
            product_name=(
                "Alpine Shell Jacket"
            ),
            quantity=500,
        )
    )

    sales_token = get_token(
        "sales",
        "Sales123!",
    )

    response = client.post(
        "/api/ai/quote",
        json={
            "message": "Large quote"
        },
        headers={
            "Authorization":
                f"Bearer {sales_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["status"]
        == "awaiting_approval"
    )

    assert data["thread_id"]
    assert data["approval_request"]

@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_sales_cannot_approve(
    mock_parse_quote_request,
):

    mock_parse_quote_request.return_value = (
        ParsedQuoteRequest(
            customer_name="Pacific Mountain Outfitters",
            product_name="Alpine Shell Jacket",
            quantity=500,
        )
    )

    sales_token = get_token(
        "sales",
        "Sales123!",
    )

    quote_response = client.post(
        "/api/ai/quote",
        json={
            "message": "Large quote"
        },
        headers={
            "Authorization":
                f"Bearer {sales_token}"
        },
    )

    thread_id = (
        quote_response.json()[
            "thread_id"
        ]
    )

    response = client.post(
        f"/api/approvals/{thread_id}",
        json={
            "decision": "approved"
        },
        headers={
            "Authorization":
                f"Bearer {sales_token}"
        },
    )

    assert response.status_code == 403

@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_manager_can_approve(
    mock_parse_quote_request,
):

    mock_parse_quote_request.return_value = (
        ParsedQuoteRequest(
            customer_name="Pacific Mountain Outfitters",
            product_name="Alpine Shell Jacket",
            quantity=500,
        )
    )

    sales_token = get_token(
        "sales",
        "Sales123!",
    )

    manager_token = get_token(
        "manager",
        "Manager123!",
    )

    quote_response = client.post(
        "/api/ai/quote",
        json={
            "message": "Large quote"
        },
        headers={
            "Authorization":
                f"Bearer {sales_token}"
        },
    )

    thread_id = (
        quote_response.json()[
            "thread_id"
        ]
    )

    response = client.post(
        f"/api/approvals/{thread_id}",
        json={
            "decision": "approved",
            "comment": "Approved by manager",
        },
        headers={
            "Authorization":
                f"Bearer {manager_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "approved"