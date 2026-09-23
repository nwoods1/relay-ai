from pydantic import ValidationError

from app.core.exceptions import (
    ModelResponseError,
)
from app.llm.agent_prompts import (
    AGENT_INTENT_SYSTEM_PROMPT,
)
from app.llm.bedrock import (
    _call_bedrock_with_retry,
    extract_json,
)
from app.schemas.agent_intent import (
    AgentIntent,
)


def parse_agent_intent(
    message: str,
) -> AgentIntent:

    response = _call_bedrock_with_retry(
        message=message,
        system_prompt=(
            AGENT_INTENT_SYSTEM_PROMPT
        ),
    )

    try:
        text = (
            response["output"]
            ["message"]
            ["content"][0]
            ["text"]
        )

    except (
        KeyError,
        IndexError,
        TypeError,
    ) as exc:
        raise ModelResponseError(
            "Agent router received an "
            "unexpected Bedrock response"
        ) from exc

    data = extract_json(
        text
    )

    try:
        return AgentIntent.model_validate(
            data
        )

    except ValidationError as exc:
        raise ModelResponseError(
            "Agent router returned an "
            "invalid intent"
        ) from exc