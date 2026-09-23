import re

from app.schemas.guardrails import (
    GuardrailResult,
)


PROMPT_INJECTION_PATTERNS = [
    r"\bignore\s+(all\s+)?previous\s+instructions\b",
    r"\bignore\s+(all\s+)?prior\s+instructions\b",
    r"\bignore\s+(all\s+)?system\s+instructions\b",
    r"\breveal\s+(your\s+)?system\s+prompt\b",
    r"\bshow\s+(me\s+)?(your\s+)?system\s+prompt\b",
    r"\bprint\s+(your\s+)?system\s+prompt\b",
    r"\bpretend\s+(you\s+are|you're)\s+(an?\s+)?admin\b",
    r"\byou\s+are\s+now\s+(an?\s+)?admin\b",
    r"\bact\s+as\s+(an?\s+)?admin\b",
    r"\bbypass\s+(the\s+)?permissions?\b",
    r"\bbypass\s+(the\s+)?authorization\b",
    r"\boverride\s+(the\s+)?permissions?\b",
    r"\boverride\s+(the\s+)?approval\s+requirements?\b",
    r"\bforget\s+(your\s+)?permission\s+rules\b",
    r"\bcall\s+(the\s+)?approval\s+tool\s+anyway\b",
    r"\bdisable\s+(the\s+)?guardrails?\b",
    r"\bignore\s+(the\s+)?guardrails?\b",
]


def check_prompt_injection(
    message: str,
) -> GuardrailResult:

    normalized = (
        message.strip().lower()
    )

    for pattern in (
        PROMPT_INJECTION_PATTERNS
    ):
        if re.search(
            pattern,
            normalized,
            re.IGNORECASE,
        ):
            return GuardrailResult(
                allowed=False,
                category=(
                    "prompt_injection"
                ),
                reason=(
                    "The request attempts "
                    "to override Relay's "
                    "instructions, permissions, "
                    "or approval controls."
                ),
            )

    return GuardrailResult(
        allowed=True
    )