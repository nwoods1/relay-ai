from app.schemas.guardrails import (
    GuardrailResult,
)


MAX_QUOTE_QUANTITY = 100_000


def validate_inventory_request(
    product_name: str | None,
) -> GuardrailResult:

    if (
        product_name is None
        or not product_name.strip()
    ):
        return GuardrailResult(
            allowed=False,
            category=(
                "invalid_tool_arguments"
            ),
            reason=(
                "A product name is required "
                "for an inventory lookup."
            ),
        )

    return GuardrailResult(
        allowed=True
    )


def validate_quote_request(
    customer_name: str | None,
    product_name: str | None,
    quantity: int | None,
) -> GuardrailResult:

    if (
        customer_name is None
        or not customer_name.strip()
    ):
        return GuardrailResult(
            allowed=False,
            category=(
                "invalid_tool_arguments"
            ),
            reason=(
                "A customer name is required."
            ),
        )

    if (
        product_name is None
        or not product_name.strip()
    ):
        return GuardrailResult(
            allowed=False,
            category=(
                "invalid_tool_arguments"
            ),
            reason=(
                "A product name is required."
            ),
        )

    if quantity is None:
        return GuardrailResult(
            allowed=False,
            category=(
                "invalid_tool_arguments"
            ),
            reason=(
                "A quantity is required."
            ),
        )

    if quantity <= 0:
        return GuardrailResult(
            allowed=False,
            category=(
                "invalid_tool_arguments"
            ),
            reason=(
                "Quote quantity must "
                "be greater than zero."
            ),
        )

    if quantity > MAX_QUOTE_QUANTITY:
        return GuardrailResult(
            allowed=False,
            category=(
                "invalid_tool_arguments"
            ),
            reason=(
                "The requested quantity "
                "is outside Relay's "
                "supported quote range."
            ),
        )

    return GuardrailResult(
        allowed=True
    )