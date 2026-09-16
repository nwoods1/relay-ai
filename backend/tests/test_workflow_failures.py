from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.exceptions import (
    ExternalServiceError,
)
from app.graph.workflow import quote_workflow
from app.main import app
from app.schemas.ai import (
    ParsedQuoteRequest,
)


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

    return response.json()[
        "access_token"
    ]


@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_bedrock_failure_routes_to_failed_workflow(
    mock_parse_quote_request,
):
    mock_parse_quote_request.side_effect = (
        ExternalServiceError(
            "Bedrock unavailable"
        )
    )

    result = quote_workflow.invoke(
        {
            "message": "Create a quote",
            "user_id": 1,
            "username": "sales",
            "user_role": "sales_rep",
        },
        config={
            "configurable": {
                "thread_id":
                    str(uuid4())
            }
        },
    )

    assert (
        result["workflow_status"]
        == "failed"
    )

    assert (
        result["failed_node"]
        == "parse_request"
    )

    assert (
        result["error_type"]
        == "ExternalServiceError"
    )


@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_api_returns_structured_workflow_failure(
    mock_parse_quote_request,
):
    mock_parse_quote_request.side_effect = (
        ExternalServiceError(
            "Bedrock unavailable"
        )
    )

    token = get_sales_token()

    response = client.post(
        "/api/ai/quote",
        json={
            "message": "Create a quote"
        },
        headers={
            "Authorization":
                f"Bearer {token}",
            "Idempotency-Key":
                str(uuid4()),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "failed"

    assert (
        data["error"]["type"]
        == "ExternalServiceError"
    )

    assert (
        data["error"]["failed_node"]
        == "parse_request"
    )


@patch(
    "app.graph.nodes.create_customer_lookup_tool"
)
@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_customer_tool_failure_is_captured(
    mock_parse,
    mock_customer_tool_factory,
):
    mock_parse.return_value = (
        ParsedQuoteRequest(
            customer_name="Pacific Mountain Outfitters",
            product_name="Alpine Shell Jacket",
            quantity=1,
        )
    )

    tool = (
        mock_customer_tool_factory.return_value
    )

    tool.invoke.side_effect = RuntimeError(
        "CRM unavailable"
    )

    result = quote_workflow.invoke(
        {
            "message": "Create quote",
            "user_id": 1,
            "username": "sales",
            "user_role": "sales_rep",
        },
        config={
            "configurable": {
                "thread_id":
                    str(uuid4())
            }
        },
    )

    assert (
        result["workflow_status"]
        == "failed"
    )

    assert (
        result["failed_node"]
        == "resolve_customer"
    )