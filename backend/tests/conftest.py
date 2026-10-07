import pytest

from app.core.config import settings


def pytest_configure(config):
    missing = [
        name
        for name, value in (
            ("SEED_SALES_PASSWORD", settings.seed_sales_password),
            ("SEED_MANAGER_PASSWORD", settings.seed_manager_password),
            ("SEED_ADMIN_PASSWORD", settings.seed_admin_password),
        )
        if not value
    ]

    if missing:
        raise pytest.UsageError(
            "Set " + ", ".join(missing) + " in .env before running tests"
        )
