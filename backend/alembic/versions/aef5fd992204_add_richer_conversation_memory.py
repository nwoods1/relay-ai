"""add richer conversation memory

Revision ID: aef5fd992204
Revises: 96252b064fe4
Create Date: 2026-09-25 19:00:48.359701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'aef5fd992204'
down_revision: Union[str, Sequence[str], None] = '96252b064fe4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "conversations",
        sa.Column(
            "last_warehouse_name",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "conversations",
        sa.Column(
            "recent_customers",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )

    op.add_column(
        "conversations",
        sa.Column(
            "recent_products",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )

    op.add_column(
        "conversations",
        sa.Column(
            "recent_quantities",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )

    op.add_column(
        "conversations",
        sa.Column(
            "recent_warehouses",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )

    op.add_column(
        "conversations",
        sa.Column(
            "recent_actions",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )

    op.add_column(
        "conversations",
        sa.Column(
            "conversation_summary",
            sa.Text(),
            nullable=True,
        ),
    )

    
    
    op.alter_column(
        "conversations",
        "recent_customers",
        server_default=None,
    )

    op.alter_column(
        "conversations",
        "recent_products",
        server_default=None,
    )

    op.alter_column(
        "conversations",
        "recent_quantities",
        server_default=None,
    )

    op.alter_column(
        "conversations",
        "recent_warehouses",
        server_default=None,
    )

    op.alter_column(
        "conversations",
        "recent_actions",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""
    
    op.drop_column('conversations', 'conversation_summary')
    op.drop_column('conversations', 'recent_actions')
    op.drop_column('conversations', 'recent_warehouses')
    op.drop_column('conversations', 'recent_quantities')
    op.drop_column('conversations', 'recent_products')
    op.drop_column('conversations', 'recent_customers')
    op.drop_column('conversations', 'last_warehouse_name')
    
