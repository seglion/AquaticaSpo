"""Add wind_url and wind_models fields to hindcast_points

Revision ID: e0e937e7c4a5
Revises: e80d637d087
Create Date: 2026-07-30 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0e937e7c4a5'
down_revision: Union[str, Sequence[str], None] = 'e80d637d087'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('hindcast_points', sa.Column('wind_url', sa.String(), nullable=True))
    op.add_column('hindcast_points', sa.Column('wind_models', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('hindcast_points', 'wind_models')
    op.drop_column('hindcast_points', 'wind_url')
