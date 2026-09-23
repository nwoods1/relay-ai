from app.schemas.guardrails import (
    GuardrailResult,
)


def validate_approval_action(
    thread_id: str | None,
) -> GuardrailResult:

    if (
        thread_id is None
        or not thread_id.strip()
    ):
        return GuardrailResult(
            allowed=False,
            category=(
                "invalid_tool_arguments"
            ),
            reason=(
                "A valid approval thread "
                "is required."
            ),
        )

    return GuardrailResult(
        allowed=True
    )