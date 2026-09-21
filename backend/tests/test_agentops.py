from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.ai import ParsedQuoteRequest
from app.core.exceptions import (
    ExternalServiceError,
)


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

    return response.json()["access_token"]


def auth_headers(
    token: str,
) -> dict:
    return {
        "Authorization":
            f"Bearer {token}"
    }


def quote_headers(
    token: str,
) -> dict:
    return {
        "Authorization":
            f"Bearer {token}",
        "Idempotency-Key":
            str(uuid4()),
    }


def test_sales_cannot_access_agentops():
    sales_token = get_token(
        "sales",
        "Sales123!",
    )

    response = client.get(
        "/api/agentops/runs",
        headers=auth_headers(
            sales_token
        ),
    )

    assert response.status_code == 403


def test_manager_can_access_agentops_runs():
    manager_token = get_token(
        "manager",
        "Manager123!",
    )

    response = client.get(
        "/api/agentops/runs",
        headers=auth_headers(
            manager_token
        ),
    )

    assert response.status_code == 200
    assert isinstance(
        response.json(),
        list,
    )


def test_admin_can_access_agentops_runs():
    admin_token = get_token(
        "admin",
        "Admin123!",
    )

    response = client.get(
        "/api/agentops/runs",
        headers=auth_headers(
            admin_token
        ),
    )

    assert response.status_code == 200
    assert isinstance(
        response.json(),
        list,
    )


def test_agentops_summary():
    manager_token = get_token(
        "manager",
        "Manager123!",
    )

    response = client.get(
        "/api/agentops/summary",
        headers=auth_headers(
            manager_token
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_runs" in data
    assert "ready_runs" in data
    assert "awaiting_approval_runs" in data
    assert "approved_runs" in data
    assert "rejected_runs" in data
    assert "failed_runs" in data
    assert "average_duration_ms" in data
    assert "total_tokens" in data


def test_unknown_workflow_run_returns_404():
    manager_token = get_token(
        "manager",
        "Manager123!",
    )

    response = client.get(
        (
            "/api/agentops/runs/"
            "does-not-exist"
        ),
        headers=auth_headers(
            manager_token
        ),
    )

    assert response.status_code == 404

@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_quote_creates_workflow_run(
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

    sales_token = get_token(
        "sales",
        "Sales123!",
    )

    quote_response = client.post(
        "/api/ai/quote",
        json={
            "message": (
                "Pacific Mountain Outfitters "
                "wants 1 Merino Wool Toque."
            )
        },
        headers=quote_headers(
            sales_token
        ),
    )

    assert quote_response.status_code == 200

    quote_data = quote_response.json()

    assert quote_data["status"] == "ready"

    thread_id = quote_data["thread_id"]

    manager_token = get_token(
        "manager",
        "Manager123!",
    )

    agentops_response = client.get(
        f"/api/agentops/runs/{thread_id}",
        headers=auth_headers(
            manager_token
        ),
    )

    assert (
        agentops_response.status_code
        == 200
    )

    data = agentops_response.json()

    assert data["thread_id"] == thread_id
    assert data["status"] == "ready"
    assert (
        data["username"]
        == "sales"
    )
    assert (
        data["operation"]
        == "create_quote"
    )

@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_approval_workflow_updates_agentops(
    mock_parse,
):
    mock_parse.return_value = (
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

    quote_response = client.post(
        "/api/ai/quote",
        json={
            "message": "Large quote"
        },
        headers=quote_headers(
            sales_token
        ),
    )

    assert quote_response.status_code == 200

    quote_data = quote_response.json()

    assert (
        quote_data["status"]
        == "awaiting_approval"
    )

    thread_id = quote_data["thread_id"]

    manager_token = get_token(
        "manager",
        "Manager123!",
    )

    before_approval = client.get(
        f"/api/agentops/runs/{thread_id}",
        headers=auth_headers(
            manager_token
        ),
    )

    assert before_approval.status_code == 200

    before_data = before_approval.json()

    assert (
        before_data["status"]
        == "awaiting_approval"
    )

    assert (
        before_data["requires_approval"]
        is True
    )

    approval_response = client.post(
        f"/api/approvals/{thread_id}",
        json={
            "decision": "approved",
            "comment": (
                "Approved during AgentOps test"
            ),
        },
        headers={
            "Authorization":
                f"Bearer {manager_token}",
            "Idempotency-Key":
                str(uuid4()),
        },
    )

    assert (
        approval_response.status_code
        == 200
    )

    after_approval = client.get(
        f"/api/agentops/runs/{thread_id}",
        headers=auth_headers(
            manager_token
        ),
    )

    assert after_approval.status_code == 200

    after_data = after_approval.json()

    assert (
        after_data["status"]
        == "approved"
    )

    assert (
        after_data["requires_approval"]
        is True
    )

@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_failed_workflow_is_visible_in_agentops(
    mock_parse,
):
    mock_parse.side_effect = (
        ExternalServiceError(
            "Bedrock unavailable"
        )
    )

    sales_token = get_token(
        "sales",
        "Sales123!",
    )

    quote_response = client.post(
        "/api/ai/quote",
        json={
            "message": "Create quote"
        },
        headers=quote_headers(
            sales_token
        ),
    )

    assert quote_response.status_code == 200

    quote_data = quote_response.json()

    assert (
        quote_data["status"]
        == "failed"
    )

    thread_id = quote_data["thread_id"]

    manager_token = get_token(
        "manager",
        "Manager123!",
    )

    response = client.get(
        f"/api/agentops/runs/{thread_id}",
        headers=auth_headers(
            manager_token
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "failed"

    assert (
        data["error_type"]
        == "ExternalServiceError"
    )

    assert (
        data["error_message"]
        == "Bedrock unavailable"
    )

    assert data["retry_count"] == 2

@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_idempotent_request_creates_one_workflow_run(
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

    sales_token = get_token(
        "sales",
        "Sales123!",
    )

    key = str(uuid4())

    headers = {
        "Authorization":
            f"Bearer {sales_token}",
        "Idempotency-Key":
            key,
    }

    body = {
        "message": (
            "Pacific Mountain Outfitters "
            "wants 1 Merino Wool Toque."
        )
    }

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

    first_data = first.json()
    second_data = second.json()

    assert (
        first_data["thread_id"]
        == second_data["thread_id"]
    )

    assert mock_parse.call_count == 1

    manager_token = get_token(
        "manager",
        "Manager123!",
    )

    runs_response = client.get(
        "/api/agentops/runs",
        headers=auth_headers(
            manager_token
        ),
    )

    assert runs_response.status_code == 200

    matching_runs = [
        run
        for run in runs_response.json()
        if run["thread_id"]
        == first_data["thread_id"]
    ]

    assert len(matching_runs) == 1