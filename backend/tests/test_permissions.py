from app.core.permissions import (
    has_permission,
)


def test_sales_can_create_quote():
    assert has_permission(
        "sales_rep",
        "quote:create",
    )


def test_sales_cannot_approve_quote():
    assert not has_permission(
        "sales_rep",
        "quote:approve",
    )


def test_manager_can_approve_quote():
    assert has_permission(
        "manager",
        "quote:approve",
    )


def test_admin_has_all_permissions():
    assert has_permission(
        "admin",
        "anything:anything",
    )