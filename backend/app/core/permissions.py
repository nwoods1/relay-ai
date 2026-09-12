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
    },

    "admin": {
        "*",
    },
}

def has_permission(
    role: str,
    permission: str,
) -> bool:

    permissions = ROLE_PERMISSIONS.get(
        role,
        set(),
    )

    return (
        "*"
        in permissions
        or permission
        in permissions
    )