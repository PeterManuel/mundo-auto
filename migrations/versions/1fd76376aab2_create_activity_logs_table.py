"""create_activity_logs_table

Revision ID: 1fd76376aab2
Revises: de6eb00baabf
Create Date: 2025-10-20 10:09:30.825830

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = '1fd76376aab2'
down_revision = 'de6eb00baabf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create activity_logs table
    op.create_table(
        'activity_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('endpoint', sa.String(), nullable=False),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('path', sa.String(), nullable=False),
        sa.Column('status_code', sa.String(), nullable=True),
        sa.Column('request_body', sa.Text(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('device_type', sa.String(), nullable=True),
        sa.Column('browser', sa.String(), nullable=True),
        sa.Column('os', sa.String(), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('processing_time_ms', sa.String(), nullable=True),
    )


def downgrade() -> None:
    # Drop the activity_logs table
    op.drop_table('activity_logs')