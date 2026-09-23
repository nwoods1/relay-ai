from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.agent_intent import (
    AgentIntent,
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

    return response.json()[
        "access_token"
    ]


def auth_headers(
    token: str,
) -> dict:

    return {
        "Authorization":
            f"Bearer {token}"
    }


def build_ready_quote_result():
    quote = SimpleNamespace(
        customer_name=(
            "Pacific Mountain Outfitters"
        ),
        product_name=(
            "Alpine Shell Jacket"
        ),
        quantity_requested=30,
        unit_price=714.99,
        subtotal=21449.70,
        approval_reasons=[],
    )

    return SimpleNamespace(
        thread_id=str(uuid4()),
        status="ready",
        quote=quote,
    )






@patch(
    "app.services.agent_service."
    "run_inventory_agent"
)
@patch(
    "app.services.agent_service."
    "parse_agent_intent"
)
def test_inventory_question_routes_to_inventory_agent(
    mock_parse_intent,
    mock_inventory_agent,
):
    mock_parse_intent.return_value = (
        AgentIntent(
            intent="check_inventory",
            product_name=(
                "Alpine Shell Jacket"
            ),
        )
    )

    mock_inventory_agent.return_value = {
        "product": {
            "product_name":
                "Alpine Shell Jacket",
            "sku":
                "JACKET-BETA-AR-M",
        },
        "inventory": {
            "total_sellable": 89,
        },
    }

    token = get_token(
        "sales",
        "Sales123!",
    )

    response = client.post(
        "/api/agent/chat",
        json={
            "message": (
                "How many Alpine Shell "
                "Jackets are available?"
            ),
            "idempotency_key":
                str(uuid4()),
        },
        headers=auth_headers(
            token
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["selected_agent"]
        == "inventory_agent"
    )

    assert (
        "89"
        in data["message"]
    )

    mock_inventory_agent.assert_called_once()






@patch(
    "app.services.agent_service."
    "run_quote_agent"
)
@patch(
    "app.services.agent_service."
    "parse_agent_intent"
)
def test_quote_question_routes_to_quote_agent(
    mock_parse_intent,
    mock_quote_agent,
):
    mock_parse_intent.return_value = (
        AgentIntent(
            intent="create_quote",
            customer_name=(
                "Pacific Mountain Outfitters"
            ),
            product_name=(
                "Alpine Shell Jacket"
            ),
            quantity=30,
        )
    )

    mock_quote_agent.return_value = (
        build_ready_quote_result()
    )

    token = get_token(
        "sales",
        "Sales123!",
    )

    response = client.post(
        "/api/agent/chat",
        json={
            "message": (
                "Can Pacific Mountain "
                "Outfitters get 30 "
                "Alpine Shell Jackets?"
            ),
            "idempotency_key":
                str(uuid4()),
        },
        headers=auth_headers(
            token
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["selected_agent"]
        == "quote_agent"
    )

    assert (
        "Pacific Mountain Outfitters"
        in data["message"]
    )

    mock_quote_agent.assert_called_once()






@patch(
    "app.services.agent_service."
    "parse_agent_intent"
)
def test_sales_cannot_list_approvals(
    mock_parse_intent,
):
    mock_parse_intent.return_value = (
        AgentIntent(
            intent="list_approvals"
        )
    )

    token = get_token(
        "sales",
        "Sales123!",
    )

    response = client.post(
        "/api/agent/chat",
        json={
            "message":
                "What approvals are pending?",
            "idempotency_key":
                str(uuid4()),
        },
        headers=auth_headers(
            token
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["selected_agent"]
        == "approval_agent"
    )

    assert (
        "don't have permission"
        in data["message"].lower()
    )






@patch(
    "app.services.agent_service."
    "list_pending_approvals"
)
@patch(
    "app.services.agent_service."
    "parse_agent_intent"
)
def test_manager_can_list_approvals(
    mock_parse_intent,
    mock_list_approvals,
):
    mock_parse_intent.return_value = (
        AgentIntent(
            intent="list_approvals"
        )
    )

    mock_list_approvals.return_value = []

    token = get_token(
        "manager",
        "Manager123!",
    )

    response = client.post(
        "/api/agent/chat",
        json={
            "message":
                "What approvals are pending?",
            "idempotency_key":
                str(uuid4()),
        },
        headers=auth_headers(
            token
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["selected_agent"]
        == "approval_agent"
    )

    assert (
        "no pending approvals"
        in data["message"].lower()
    )















@patch(
    "app.services.agent_service."
    "run_quote_agent"
)
@patch(
    "app.services.agent_service."
    "run_inventory_agent"
)
@patch(
    "app.services.agent_service."
    "parse_agent_intent"
)
def test_previous_product_resolves_across_turns(
    mock_parse_intent,
    mock_inventory_agent,
    mock_quote_agent,
):
    mock_parse_intent.side_effect = [
        AgentIntent(
            intent="check_inventory",
            product_name=(
                "Alpine Shell Jacket"
            ),
        ),
        AgentIntent(
            intent="create_quote",
            customer_name=(
                "Pacific Mountain Outfitters"
            ),
            product_name=None,
            quantity=30,
            reference_previous_product=True,
        ),
    ]

    mock_inventory_agent.return_value = {
        "product": {
            "product_name":
                "Alpine Shell Jacket",
            "sku":
                "JACKET-BETA-AR-M",
        },
        "inventory": {
            "total_sellable": 89,
        },
    }

    mock_quote_agent.return_value = (
        build_ready_quote_result()
    )

    token = get_token(
        "sales",
        "Sales123!",
    )

    first = client.post(
        "/api/agent/chat",
        json={
            "message": (
                "How many Alpine Shell "
                "Jackets are available?"
            ),
            "idempotency_key":
                str(uuid4()),
        },
        headers=auth_headers(
            token
        ),
    )

    assert first.status_code == 200

    first_data = first.json()

    assert (
        first_data["selected_agent"]
        == "inventory_agent"
    )

    conversation_id = (
        first_data["conversation_id"]
    )

    second = client.post(
        "/api/agent/chat",
        json={
            "message": (
                "Can Pacific Mountain "
                "Outfitters get 30 of them?"
            ),
            "conversation_id":
                conversation_id,
            "idempotency_key":
                str(uuid4()),
        },
        headers=auth_headers(
            token
        ),
    )

    assert second.status_code == 200

    second_data = second.json()

    assert (
        second_data["selected_agent"]
        == "quote_agent"
    )

    mock_quote_agent.assert_called_once()

    call_kwargs = (
        mock_quote_agent.call_args.kwargs
    )

    resolved_intent = (
        call_kwargs["intent"]
    )

    assert (
        resolved_intent.product_name
        == "Alpine Shell Jacket"
    )

    assert (
        resolved_intent.customer_name
        == "Pacific Mountain Outfitters"
    )

    assert (
        resolved_intent.quantity
        == 30
    )






@patch(
    "app.services.agent_service."
    "run_quote_agent"
)
@patch(
    "app.services.agent_service."
    "run_inventory_agent"
)
@patch(
    "app.services.agent_service."
    "parse_agent_intent"
)
def test_new_conversation_does_not_inherit_context(
    mock_parse_intent,
    mock_inventory_agent,
    mock_quote_agent,
):
    mock_parse_intent.side_effect = [
        AgentIntent(
            intent="check_inventory",
            product_name=(
                "Alpine Shell Jacket"
            ),
        ),
        AgentIntent(
            intent="create_quote",
            customer_name=(
                "Pacific Mountain Outfitters"
            ),
            product_name=None,
            quantity=30,
            reference_previous_product=True,
        ),
    ]

    mock_inventory_agent.return_value = {
        "product": {
            "product_name":
                "Alpine Shell Jacket",
            "sku":
                "JACKET-BETA-AR-M",
        },
        "inventory": {
            "total_sellable": 89,
        },
    }

    token = get_token(
        "sales",
        "Sales123!",
    )

    first = client.post(
        "/api/agent/chat",
        json={
            "message": (
                "How many Alpine Shell "
                "Jackets are available?"
            ),
            "idempotency_key":
                str(uuid4()),
        },
        headers=auth_headers(
            token
        ),
    )

    assert first.status_code == 200

    
    
    
    
    second = client.post(
        "/api/agent/chat",
        json={
            "message": (
                "Can Pacific Mountain "
                "Outfitters get 30 of them?"
            ),
            "conversation_id": None,
            "idempotency_key":
                str(uuid4()),
        },
        headers=auth_headers(
            token
        ),
    )

    assert second.status_code == 200

    data = second.json()

    assert (
        data["selected_agent"]
        == "quote_agent"
    )

    assert (
        "which product"
        in data["message"].lower()
    )

    mock_quote_agent.assert_not_called()






@patch(
    "app.services.agent_service."
    "parse_agent_intent"
)
def test_general_message_routes_to_general_agent(
    mock_parse_intent,
):
    mock_parse_intent.return_value = (
        AgentIntent(
            intent="general"
        )
    )

    token = get_token(
        "sales",
        "Sales123!",
    )

    response = client.post(
        "/api/agent/chat",
        json={
            "message":
                "What can you help me with?",
            "idempotency_key":
                str(uuid4()),
        },
        headers=auth_headers(
            token
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["selected_agent"]
        == "general_agent"
    )