import pytest

from app.guardrails.policy import (
    can_perform_action,
)
from app.guardrails.prompt_injection import (
    check_prompt_injection,
)
from app.guardrails.tool_validation import (
    validate_inventory_request,
    validate_quote_request,
)
from tests.evals.cases import (
    PROMPT_INJECTION_CASES,
    SAFE_PROMPT_CASES,
)


@pytest.mark.parametrize(
    "message",
    PROMPT_INJECTION_CASES,
)
def test_prompt_injection_is_blocked(
    message,
):
    result = check_prompt_injection(
        message
    )

    assert result.allowed is False

    assert (
        result.category
        == "prompt_injection"
    )


@pytest.mark.parametrize(
    "message",
    SAFE_PROMPT_CASES,
)
def test_normal_business_requests_are_not_blocked(
    message,
):
    result = check_prompt_injection(
        message
    )

    assert result.allowed is True


def test_sales_can_create_quote():
    assert can_perform_action(
        "sales_rep",
        "create_quote",
    )


def test_sales_can_check_inventory():
    assert can_perform_action(
        "sales_rep",
        "check_inventory",
    )


def test_sales_cannot_list_approvals():
    assert not can_perform_action(
        "sales_rep",
        "list_approvals",
    )


def test_sales_cannot_approve_quote():
    assert not can_perform_action(
        "sales_rep",
        "approve_quote",
    )


def test_manager_can_list_approvals():
    assert can_perform_action(
        "manager",
        "list_approvals",
    )


def test_manager_can_approve_quote():
    assert can_perform_action(
        "manager",
        "approve_quote",
    )


def test_admin_can_perform_any_known_action():
    assert can_perform_action(
        "admin",
        "approve_quote",
    )

    assert can_perform_action(
        "admin",
        "create_quote",
    )

    assert can_perform_action(
        "admin",
        "check_inventory",
    )


def test_inventory_requires_product():
    result = (
        validate_inventory_request(
            None
        )
    )

    assert result.allowed is False


def test_quote_requires_customer():
    result = (
        validate_quote_request(
            customer_name=None,
            product_name=(
                "Alpine Shell Jacket"
            ),
            quantity=10,
        )
    )

    assert result.allowed is False


def test_quote_requires_product():
    result = (
        validate_quote_request(
            customer_name=(
                "Pacific Mountain Outfitters"
            ),
            product_name=None,
            quantity=10,
        )
    )

    assert result.allowed is False


def test_quote_requires_quantity():
    result = (
        validate_quote_request(
            customer_name=(
                "Pacific Mountain Outfitters"
            ),
            product_name=(
                "Alpine Shell Jacket"
            ),
            quantity=None,
        )
    )

    assert result.allowed is False


def test_zero_quantity_is_blocked():
    result = (
        validate_quote_request(
            customer_name=(
                "Pacific Mountain Outfitters"
            ),
            product_name=(
                "Alpine Shell Jacket"
            ),
            quantity=0,
        )
    )

    assert result.allowed is False


def test_negative_quantity_is_blocked():
    result = (
        validate_quote_request(
            customer_name=(
                "Pacific Mountain Outfitters"
            ),
            product_name=(
                "Alpine Shell Jacket"
            ),
            quantity=-5,
        )
    )

    assert result.allowed is False


def test_extreme_quantity_is_blocked():
    result = (
        validate_quote_request(
            customer_name=(
                "Pacific Mountain Outfitters"
            ),
            product_name=(
                "Alpine Shell Jacket"
            ),
            quantity=1_000_000_000,
        )
    )

    assert result.allowed is False


def test_valid_quote_arguments_are_allowed():
    result = (
        validate_quote_request(
            customer_name=(
                "Pacific Mountain Outfitters"
            ),
            product_name=(
                "Alpine Shell Jacket"
            ),
            quantity=30,
        )
    )

    assert result.allowed is True