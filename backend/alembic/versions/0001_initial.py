"""initial

Revision ID: 0001
Revises: 
Create Date: 2025-01-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('email', sa.String(), unique=True, index=True, nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
    )
    op.create_table(
        'protocols',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), default='draft'),
        sa.Column('pi_id', sa.String(), nullable=True),
    )


def downgrade():
    op.drop_table('protocols')
    op.drop_table('users')
