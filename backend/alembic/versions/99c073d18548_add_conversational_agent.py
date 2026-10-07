"""add conversational agent

Revision ID: 99c073d18548
Revises: 7b88acc0d983
Create Date: 2026-09-20 19:58:21.350478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '99c073d18548'
down_revision: Union[str, Sequence[str], None] = '7b88acc0d983'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.create_table('conversations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('conversation_id', sa.String(length=100), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_conversation_id'), 'conversations', ['conversation_id'], unique=True)
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)
    op.create_table('conversation_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('conversation_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('message_type', sa.String(length=50), nullable=False),
    sa.Column('workflow_thread_id', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_messages_conversation_id'), 'conversation_messages', ['conversation_id'], unique=False)
    


def downgrade() -> None:
    """Downgrade schema."""
    
    op.drop_index(op.f('ix_conversation_messages_conversation_id'), table_name='conversation_messages')
    op.drop_table('conversation_messages')
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_conversation_id'), table_name='conversations')
    op.drop_table('conversations')
    
