"""add pending conversation actions

Revision ID: 9f3b9ba1880c
Revises: 99c073d18548
Create Date: 2026-09-21 17:47:20.202201

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



revision: str = '9f3b9ba1880c'
down_revision: Union[str, Sequence[str], None] = '99c073d18548'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.add_column('conversations', sa.Column('pending_action', sa.String(length=100), nullable=True))
    op.add_column('conversations', sa.Column('pending_thread_id', sa.String(length=100), nullable=True))
    


def downgrade() -> None:
    """Downgrade schema."""
    
    op.drop_column('conversations', 'pending_thread_id')
    op.drop_column('conversations', 'pending_action')
    
