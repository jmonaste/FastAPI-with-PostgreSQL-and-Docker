"""Add created_at and updated_at columns to vehicle_types

Revision ID: 7c4a4f844dc4
Revises: <ID de la migración anterior>
Create Date: 2024-09-28 13:49:01.678670

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7c4a4f844dc4'
down_revision: Union[str, None] = None  # Cambia esto
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Añadir columnas created_at y updated_at a vehicle_types
    op.add_column('vehicle_types', sa.Column('created_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('vehicle_types', sa.Column('updated_at', sa.TIMESTAMP(), nullable=True))


def downgrade() -> None:
    # Eliminar columnas created_at y updated_at de vehicle_types
    op.drop_column('vehicle_types', 'created_at')
    op.drop_column('vehicle_types', 'updated_at')
