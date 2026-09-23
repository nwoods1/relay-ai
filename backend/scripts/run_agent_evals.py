from app.agents.router import (
    select_agent,
)
from app.guardrails.policy import (
    can_perform_action,
)
from app.guardrails.prompt_injection import (
    check_prompt_injection,
)
from app.guardrails.response_validation import (
    validate_grounded_response,
)
from app.schemas.agent_intent import (
    AgentIntent,
)
from tests.evals.cases import (
    PROMPT_INJECTION_CASES,
    ROUTING_EVAL_CASES,
    SAFE_PROMPT_CASES,
)


def calculate_rate(
    passed: int,
    total: int,
) -> float:

    if total == 0:
        return 0.0

    return (
        passed
        / total
        * 100
    )


def run_routing_evals():
    passed = 0

    for case in (
        ROUTING_EVAL_CASES
    ):
        intent = AgentIntent(
            intent=case["intent"]
        )

        actual = select_agent(
            intent
        )

        if (
            actual
            == case[
                "expected_agent"
            ]
        ):
            passed += 1

    return (
        passed,
        len(
            ROUTING_EVAL_CASES
        ),
    )


def run_prompt_injection_evals():
    passed = 0
    total = 0

    for message in (
        PROMPT_INJECTION_CASES
    ):
        total += 1

        result = (
            check_prompt_injection(
                message
            )
        )

        if not result.allowed:
            passed += 1

    for message in (
        SAFE_PROMPT_CASES
    ):
        total += 1

        result = (
            check_prompt_injection(
                message
            )
        )

        if result.allowed:
            passed += 1

    return (
        passed,
        total,
    )


def run_authorization_evals():
    cases = [
        (
            "sales_rep",
            "create_quote",
            True,
        ),
        (
            "sales_rep",
            "check_inventory",
            True,
        ),
        (
            "sales_rep",
            "list_approvals",
            False,
        ),
        (
            "sales_rep",
            "approve_quote",
            False,
        ),
        (
            "manager",
            "list_approvals",
            True,
        ),
        (
            "manager",
            "approve_quote",
            True,
        ),
        (
            "admin",
            "approve_quote",
            True,
        ),
    ]

    passed = 0

    for (
        role,
        action,
        expected,
    ) in cases:

        actual = (
            can_perform_action(
                user_role=role,
                action=action,
            )
        )

        if actual == expected:
            passed += 1

    return (
        passed,
        len(cases),
    )


def run_grounding_evals():
    cases = [
        (
            "There are 89 units.",
            True,
            True,
        ),
        (
            "There are 89 units.",
            False,
            False,
        ),
        (
            "The price is $714.99.",
            True,
            True,
        ),
        (
            "The price is $714.99.",
            False,
            False,
        ),
        (
            (
                "I can help with "
                "inventory."
            ),
            False,
            True,
        ),
    ]

    passed = 0

    for (
        message,
        grounded,
        expected,
    ) in cases:

        result = (
            validate_grounded_response(
                message=message,
                grounded=grounded,
            )
        )

        if (
            result.allowed
            == expected
        ):
            passed += 1

    return (
        passed,
        len(cases),
    )


def print_result(
    name: str,
    result,
):
    passed, total = result

    rate = calculate_rate(
        passed,
        total,
    )

    print(
        f"{name}: "
        f"{passed}/{total} "
        f"({rate:.1f}%)"
    )


def main():
    print(
        "\nRelay AI Agent Evaluation"
    )

    print(
        "=" * 40
    )

    print_result(
        "Routing accuracy",
        run_routing_evals(),
    )

    print_result(
        "Guardrail pass rate",
        run_prompt_injection_evals(),
    )

    print_result(
        "Authorization pass rate",
        run_authorization_evals(),
    )

    print_result(
        "Grounding pass rate",
        run_grounding_evals(),
    )

    print(
        "=" * 40
    )


if __name__ == "__main__":
    main()