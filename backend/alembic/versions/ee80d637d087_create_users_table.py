"""Create users table

Revision ID: 8e80d637d087
Revises: a83af5a6ce56
Create Date: 2025-06-30 17:34:21.470038

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e80d637d087'
down_revision: Union[str, Sequence[str], None] = 'a83af5a6ce56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ports',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('country', sa.String(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
    )
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(length=50), nullable=False, unique=True),
        sa.Column('email', sa.String(length=100), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_admin', sa.Boolean, nullable=False, default=False),
        sa.Column('is_employee', sa.Boolean, nullable=False, default=False),
    )

    # Tabla temporal para hacer inserts
    users_table = table(
        'users',
        column('username', String),
        column('email', String),
        column('hashed_password', String),
        column('is_admin', Boolean),
        column('is_employee', Boolean),
    )

    # Inserta usuario admin y otro normal
    op.bulk_insert(users_table,
        [
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'hashed_password': 'hashed-adminpassword',  # Usa aquí tu función de hash real
                'is_admin': True,
                'is_employee': False,
            },
            {
                'username': 'user',
                'email': 'user@example.com',
                'hashed_password': 'hashed-userpassword',
                'is_admin': False,
                'is_employee': True,
            }
        ]
    )


def downgrade() -> None:
    op.drop_table('ports')

