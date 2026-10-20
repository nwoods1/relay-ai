from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


client = TestClient(app)


DASHBOARD_PATHS = [
    "/api/dashboard/overview",
    "/api/dashboard/quotes",
    "/api/dashboard/inventory",
    "/api/dashboard/warehouses",
    "/api/dashboard/approvals",
    "/api/dashboard/activity",
]


SALES_ALLOWED_DASHBOARD_PATHS = [
    "/api/dashboard/inventory",
    "/api/dashboard/warehouses",
]


SALES_RESTRICTED_DASHBOARD_PATHS = [
    "/api/dashboard/overview",
    "/api/dashboard/quotes",
    "/api/dashboard/approvals",
    "/api/dashboard/activity",
]


def get_token(
    username: str,
    password: str,
) -> str:
    response = client.post(
        "/api/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def auth_headers(
    token: str,
) -> dict:
    return {
        "Authorization":
            f"Bearer {token}"
    }


def manager_headers() -> dict:
    return auth_headers(
        get_token(
            "manager",
            settings.seed_manager_password,
        )
    )


def sales_headers() -> dict:
    return auth_headers(
        get_token(
            "sales",
            settings.seed_sales_password,
        )
    )


def test_dashboard_requires_authentication():
    for path in DASHBOARD_PATHS:
        response = client.get(path)

        assert response.status_code == 401, path


def test_sales_can_access_inventory_dashboard():
    headers = sales_headers()

    for path in (
        SALES_ALLOWED_DASHBOARD_PATHS
    ):
        response = client.get(
            path,
            headers=headers,
        )

        assert response.status_code == 200, path


def test_sales_cannot_access_manager_dashboard():
    headers = sales_headers()

    for path in (
        SALES_RESTRICTED_DASHBOARD_PATHS
    ):
        response = client.get(
            path,
            headers=headers,
        )

        assert response.status_code == 403, path


def test_manager_and_admin_can_access_dashboard():
    admin_headers = auth_headers(
        get_token(
            "admin",
            settings.seed_admin_password,
        )
    )

    for headers in (
        manager_headers(),
        admin_headers,
    ):
        for path in DASHBOARD_PATHS:
            response = client.get(
                path,
                headers=headers,
            )

            assert response.status_code == 200, path


def test_dashboard_does_not_call_bedrock_or_langgraph():
    headers = manager_headers()

    with (
        patch(
            "app.llm.bedrock.bedrock_client"
        ) as bedrock_mock,
        patch(
            "app.graph.workflow.quote_workflow"
        ) as graph_mock,
    ):
        for path in DASHBOARD_PATHS:
            response = client.get(
                path,
                headers=headers,
            )

            assert response.status_code == 200, path

    bedrock_mock.converse.assert_not_called()
    graph_mock.invoke.assert_not_called()
    graph_mock.stream.assert_not_called()


def test_dashboard_overview_workflow_counts_are_consistent():
    response = client.get(
        "/api/dashboard/overview",
        headers=manager_headers(),
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["total_sellable_inventory"]
        <= data["total_physical_inventory"]
    )

    assert (
        data["active_workflows"]
        + data["completed_workflows"]
        + data["failed_workflows"]
        <= data["total_workflows"]
    )


def test_sales_can_read_inventory_data():
    response = client.get(
        "/api/dashboard/inventory",
        params={
            "search":
                "JACKET-BETA-AR-M"
        },
        headers=sales_headers(),
    )

    assert response.status_code == 200

    items = response.json()["items"]

    shell = next(
        item
        for item in items
        if item["sku"]
        == "JACKET-BETA-AR-M"
    )

    assert (
        shell["physical_quantity"]
        == 105
    )

    assert (
        shell["reserved_quantity"]
        == 16
    )

    assert (
        shell["sellable_quantity"]
        == 89
    )


def test_dashboard_inventory_shell_totals():
    headers = manager_headers()

    for search in (
        "shell",
        "JACKET-BETA-AR-M",
    ):
        response = client.get(
            "/api/dashboard/inventory",
            params={
                "search":
                    search
            },
            headers=headers,
        )

        assert response.status_code == 200

        items = response.json()["items"]

        shell = next(
            item
            for item in items
            if item["sku"]
            == "JACKET-BETA-AR-M"
        )

        assert (
            shell["physical_quantity"]
            == 105
        )

        assert (
            shell["reserved_quantity"]
            == 16
        )

        assert (
            shell["sellable_quantity"]
            == 89
        )


def test_dashboard_van_warehouse_shell_inventory():
    response = client.get(
        "/api/dashboard/warehouses",
        headers=manager_headers(),
    )

    assert response.status_code == 200

    van = next(
        warehouse
        for warehouse
        in response.json()["items"]
        if warehouse["code"] == "VAN"
    )

    shell = next(
        row
        for row
        in van["inventory"]
        if row["sku"]
        == "JACKET-BETA-AR-M"
    )

    assert (
        shell["physical_quantity"]
        == 42
    )

    assert (
        shell["reserved_quantity"]
        == 7
    )

    assert (
        shell["sellable_quantity"]
        == 35
    )

    assert (
        van["total_physical"]
        == sum(
            row["physical_quantity"]
            for row
            in van["inventory"]
        )
    )


def test_sales_can_read_warehouse_data():
    response = client.get(
        "/api/dashboard/warehouses",
        headers=sales_headers(),
    )

    assert response.status_code == 200

    items = response.json()["items"]

    assert len(items) > 0

    assert any(
        warehouse["code"]
        == "VAN"
        for warehouse in items
    )


def test_dashboard_quotes_newest_first_and_filtered():
    headers = manager_headers()

    response = client.get(
        "/api/dashboard/quotes",
        params={
            "limit":
                5
        },
        headers=headers,
    )

    assert response.status_code == 200

    items = response.json()["items"]

    assert len(items) <= 5

    started = [
        item["started_at"]
        for item in items
    ]

    assert started == sorted(
        started,
        reverse=True,
    )

    response = client.get(
        "/api/dashboard/quotes",
        params={
            "status":
                "failed"
        },
        headers=headers,
    )

    assert response.status_code == 200

    assert all(
        item["status"] == "failed"
        for item
        in response.json()["items"]
    )


def test_dashboard_limits_are_bounded():
    headers = manager_headers()

    for path in (
        "/api/dashboard/quotes",
        "/api/dashboard/approvals",
        "/api/dashboard/activity",
    ):
        for limit in (
            0,
            101,
        ):
            response = client.get(
                path,
                params={
                    "limit":
                        limit
                },
                headers=headers,
            )

            assert response.status_code == 422, path


def test_dashboard_approvals_status_filter():
    headers = manager_headers()

    for status in (
        "pending",
        "approved",
        "rejected",
    ):
        response = client.get(
            "/api/dashboard/approvals",
            params={
                "status":
                    status
            },
            headers=headers,
        )

        assert response.status_code == 200

        assert all(
            item["status"] == status
            for item
            in response.json()["items"]
        )

    response = client.get(
        "/api/dashboard/approvals",
        params={
            "status":
                "bogus"
        },
        headers=headers,
    )

    assert response.status_code == 422


def test_dashboard_activity_newest_first():
    response = client.get(
        "/api/dashboard/activity",
        params={
            "limit":
                10
        },
        headers=manager_headers(),
    )

    assert response.status_code == 200

    items = response.json()["items"]

    created = [
        item["created_at"]
        for item in items
    ]

    assert created == sorted(
        created,
        reverse=True,
    )

    for item in items:
        assert item["thread_id"]
        assert item["operation"]
        assert item["username"]