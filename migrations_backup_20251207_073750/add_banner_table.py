"""
Add banners table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_banner_table'
down_revision = 'fa2909e8c3ff'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'banners',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('image_url', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=True)
    )

def downgrade():
    op.drop_table('banners')
