from app.schemas.agent_intent import (
    AgentIntent,
)


def select_agent(
    intent: AgentIntent,
) -> str:

    if intent.intent == "create_quote":
        return "quote_agent"

    if intent.intent == "check_inventory":
        return "inventory_agent"

    if intent.intent in {
        "list_approvals",
        "approve_quote",
        "reject_quote",
    }:
        return "approval_agent"

    if intent.intent in {
        "confirm_action",
        "reject_action",
    }:
        return "conversation_action"

    return "general_agent"