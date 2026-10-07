"""add agentops workflow monitoring

Revision ID: 7b88acc0d983
Revises: 47b4fd024a82
Create Date: 2026-09-16 13:22:08.505370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '7b88acc0d983'
down_revision: Union[str, Sequence[str], None] = '47b4fd024a82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.create_table('workflow_runs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('thread_id', sa.String(length=100), nullable=False),
    sa.Column('operation', sa.String(length=100), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('user_role', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('current_node', sa.String(length=100), nullable=True),
    sa.Column('requires_approval', sa.Boolean(), nullable=False),
    sa.Column('error_type', sa.String(length=100), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('retry_count', sa.Integer(), nullable=False),
    sa.Column('input_tokens', sa.Integer(), nullable=False),
    sa.Column('output_tokens', sa.Integer(), nullable=False),
    sa.Column('total_tokens', sa.Integer(), nullable=False),
    sa.Column('llm_latency_ms', sa.Float(), nullable=True),
    sa.Column('duration_ms', sa.Float(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=False),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_runs_operation'), 'workflow_runs', ['operation'], unique=False)
    op.create_index(op.f('ix_workflow_runs_status'), 'workflow_runs', ['status'], unique=False)
    op.create_index(op.f('ix_workflow_runs_thread_id'), 'workflow_runs', ['thread_id'], unique=True)
    op.create_index(op.f('ix_workflow_runs_user_id'), 'workflow_runs', ['user_id'], unique=False)
    op.create_table('workflow_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('workflow_run_id', sa.Integer(), nullable=False),
    sa.Column('event_type', sa.String(length=100), nullable=False),
    sa.Column('node_name', sa.String(length=100), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('metadata_json', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['workflow_run_id'], ['workflow_runs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_events_event_type'), 'workflow_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_workflow_events_workflow_run_id'), 'workflow_events', ['workflow_run_id'], unique=False)
    


def downgrade() -> None:
    """Downgrade schema."""
    
    op.drop_index(op.f('ix_workflow_events_workflow_run_id'), table_name='workflow_events')
    op.drop_index(op.f('ix_workflow_events_event_type'), table_name='workflow_events')
    op.drop_table('workflow_events')
    op.drop_index(op.f('ix_workflow_runs_user_id'), table_name='workflow_runs')
    op.drop_index(op.f('ix_workflow_runs_thread_id'), table_name='workflow_runs')
    op.drop_index(op.f('ix_workflow_runs_status'), table_name='workflow_runs')
    op.drop_index(op.f('ix_workflow_runs_operation'), table_name='workflow_runs')
    op.drop_table('workflow_runs')
    
