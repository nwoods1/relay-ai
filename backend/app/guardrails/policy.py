ROLE_PERMISSIONS = {
    "sales_rep": {
        "quote:create",
        "customer:read",
        "product:read",
        "inventory:read",
        "pricing:read",
    },
    "manager": {
        "quote:create",
        "quote:approve",
        "customer:read",
        "product:read",
        "inventory:read",
        "pricing:read",
        "monitoring:read",
    },
    "admin": {
        "*",
    },
}


ACTION_PERMISSIONS = {
    "create_quote": (
        "quote:create"
    ),
    "check_inventory": (
        "inventory:read"
    ),
    "list_approvals": (
        "quote:approve"
    ),
    "approve_quote": (
        "quote:approve"
    ),
    "reject_quote": (
        "quote:approve"
    ),
    "submit_quote_approval": (
        "quote:create"
    ),
}


def has_permission(
    user_role: str,
    permission: str,
) -> bool:

    permissions = (
        ROLE_PERMISSIONS.get(
            user_role,
            set(),
        )
    )

    return (
        "*"
        in permissions
        or permission
        in permissions
    )


def can_perform_action(
    user_role: str,
    action: str,
) -> bool:

    required_permission = (
        ACTION_PERMISSIONS.get(
            action
        )
    )

    if required_permission is None:
        return True

    return has_permission(
        user_role=user_role,
        permission=required_permission,
    )