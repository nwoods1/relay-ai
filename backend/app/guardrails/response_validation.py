import re

from app.schemas.guardrails import (
    GuardrailResult,
)


NUMBER_PATTERN = re.compile(
    r"""
    (?:
        \$\s*
    )?
    \d
    [\d,]*
    (?:
        \.\d+
    )?
    """,
    re.VERBOSE,
)


def response_contains_numbers(
    message: str,
) -> bool:

    return bool(
        NUMBER_PATTERN.search(
            message
        )
    )


def validate_grounded_response(
    message: str,
    grounded: bool,
) -> GuardrailResult:

    if (
        response_contains_numbers(
            message
        )
        and not grounded
    ):
        return GuardrailResult(
            allowed=False,
            category=(
                "unsafe_output"
            ),
            reason=(
                "The response contains "
                "business numbers that were "
                "not verified by a tool or "
                "workflow result."
            ),
        )

    return GuardrailResult(
        allowed=True
    )