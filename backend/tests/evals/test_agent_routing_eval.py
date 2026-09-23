import pytest

from app.agents.router import (
    select_agent,
)
from app.schemas.agent_intent import (
    AgentIntent,
)
from tests.evals.cases import (
    ROUTING_EVAL_CASES,
)


@pytest.mark.parametrize(
    "case",
    ROUTING_EVAL_CASES,
)
def test_agent_routing_eval(
    case,
):
    intent = AgentIntent(
        intent=case[
            "intent"
        ]
    )

    selected_agent = (
        select_agent(
            intent
        )
    )

    assert (
        selected_agent
        == case[
            "expected_agent"
        ]
    )


def test_confirmation_routes_to_conversation_action():
    intent = AgentIntent(
        intent="confirm_action"
    )

    assert (
        select_agent(
            intent
        )
        == "conversation_action"
    )


def test_rejection_routes_to_conversation_action():
    intent = AgentIntent(
        intent="reject_action"
    )

    assert (
        select_agent(
            intent
        )
        == "conversation_action"
    )


def test_approve_quote_routes_to_approval_agent():
    intent = AgentIntent(
        intent="approve_quote"
    )

    assert (
        select_agent(
            intent
        )
        == "approval_agent"
    )


def test_reject_quote_routes_to_approval_agent():
    intent = AgentIntent(
        intent="reject_quote"
    )

    assert (
        select_agent(
            intent
        )
        == "approval_agent"
    )