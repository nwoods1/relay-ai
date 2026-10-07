"""add approvals table

Revision ID: 120ef387e3c9
Revises: 26732180c287
Create Date: 2026-09-14 16:34:42.638104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '120ef387e3c9'
down_revision: Union[str, Sequence[str], None] = '26732180c287'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.create_table('approvals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('thread_id', sa.String(length=100), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('requested_by_user_id', sa.Integer(), nullable=False),
    sa.Column('decided_by_user_id', sa.Integer(), nullable=True),
    sa.Column('decision_comment', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('decided_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['decided_by_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['requested_by_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_approvals_thread_id'), 'approvals', ['thread_id'], unique=True)
    


def downgrade() -> None:
    """Downgrade schema."""
    
    op.drop_index(op.f('ix_approvals_thread_id'), table_name='approvals')
    op.drop_table('approvals')
    
