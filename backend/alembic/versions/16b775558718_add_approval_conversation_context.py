"""add approval conversation context

Revision ID: 16b775558718
Revises: 87151bd6a823
Create Date: 2026-09-22 19:55:56.752262

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '16b775558718'
down_revision: Union[str, Sequence[str], None] = '87151bd6a823'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.add_column('conversations', sa.Column('last_approval_thread_id', sa.String(length=100), nullable=True))
    op.add_column('conversations', sa.Column('last_approval_action', sa.String(length=50), nullable=True))
    


def downgrade() -> None:
    """Downgrade schema."""
    
    op.drop_column('conversations', 'last_approval_action')
    op.drop_column('conversations', 'last_approval_thread_id')
    
