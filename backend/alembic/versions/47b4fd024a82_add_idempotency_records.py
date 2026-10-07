"""add idempotency records

Revision ID: 47b4fd024a82
Revises: 120ef387e3c9
Create Date: 2026-09-15 11:26:21.341701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '47b4fd024a82'
down_revision: Union[str, Sequence[str], None] = '120ef387e3c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.create_table('idempotency_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=255), nullable=False),
    sa.Column('operation', sa.String(length=100), nullable=False),
    sa.Column('request_hash', sa.String(length=64), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('response_json', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_idempotency_records_key'), 'idempotency_records', ['key'], unique=True)
    op.create_index(op.f('ix_idempotency_records_operation'), 'idempotency_records', ['operation'], unique=False)
    


def downgrade() -> None:
    """Downgrade schema."""
    
    op.drop_index(op.f('ix_idempotency_records_operation'), table_name='idempotency_records')
    op.drop_index(op.f('ix_idempotency_records_key'), table_name='idempotency_records')
    op.drop_table('idempotency_records')
    
