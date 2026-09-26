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
    op.create_table('checkpoint_migrations',
    sa.Column('v', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('v', name=op.f('checkpoint_migrations_pkey'))
    )
    op.create_table('checkpoint_blobs',
    sa.Column('thread_id', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('checkpoint_ns', sa.TEXT(), server_default=sa.text("''::text"), autoincrement=False, nullable=False),
    sa.Column('channel', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('version', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('type', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('blob', postgresql.BYTEA(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('thread_id', 'checkpoint_ns', 'channel', 'version', name=op.f('checkpoint_blobs_pkey'))
    )
    op.create_index(op.f('checkpoint_blobs_thread_id_idx'), 'checkpoint_blobs', ['thread_id'], unique=False)
    op.create_table('checkpoint_writes',
    sa.Column('thread_id', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('checkpoint_ns', sa.TEXT(), server_default=sa.text("''::text"), autoincrement=False, nullable=False),
    sa.Column('checkpoint_id', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('task_id', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('idx', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('channel', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('type', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('blob', postgresql.BYTEA(), autoincrement=False, nullable=False),
    sa.Column('task_path', sa.TEXT(), server_default=sa.text("''::text"), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('thread_id', 'checkpoint_ns', 'checkpoint_id', 'task_id', 'idx', name=op.f('checkpoint_writes_pkey'))
    )
    op.create_index(op.f('checkpoint_writes_thread_id_idx'), 'checkpoint_writes', ['thread_id'], unique=False)
    op.create_table('checkpoints',
    sa.Column('thread_id', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('checkpoint_ns', sa.TEXT(), server_default=sa.text("''::text"), autoincrement=False, nullable=False),
    sa.Column('checkpoint_id', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('parent_checkpoint_id', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('type', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('checkpoint', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('thread_id', 'checkpoint_ns', 'checkpoint_id', name=op.f('checkpoints_pkey'))
    )
    op.create_index(op.f('checkpoints_thread_id_idx'), 'checkpoints', ['thread_id'], unique=False)
    
