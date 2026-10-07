"""add shared agent conversation context

Revision ID: 87151bd6a823
Revises: 9f3b9ba1880c
Create Date: 2026-09-21 19:30:04.683544

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '87151bd6a823'
down_revision: Union[str, Sequence[str], None] = '9f3b9ba1880c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.add_column('conversations', sa.Column('last_customer_name', sa.String(length=255), nullable=True))
    op.add_column('conversations', sa.Column('last_product_name', sa.String(length=255), nullable=True))
    op.add_column('conversations', sa.Column('last_quantity', sa.Integer(), nullable=True))
    


def downgrade() -> None:
    """Downgrade schema."""
    
    op.drop_column('conversations', 'last_quantity')
    op.drop_column('conversations', 'last_product_name')
    op.drop_column('conversations', 'last_customer_name')
    
