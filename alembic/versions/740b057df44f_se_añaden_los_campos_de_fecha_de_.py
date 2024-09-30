"""Se añaden los campos de fecha de creacion y de modificacion a las tablas de modelo y marca

Revision ID: 740b057df44f
Revises: 7c4a4f844dc4
Create Date: 2024-09-29 13:39:30.513419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '740b057df44f'
down_revision: Union[str, None] = '7c4a4f844dc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Añadir columnas created_at y updated_at a vehicle_types
    op.add_column('brands', sa.Column('created_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('brands', sa.Column('updated_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('models', sa.Column('created_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('models', sa.Column('updated_at', sa.TIMESTAMP(), nullable=True))

def downgrade() -> None:
    # Eliminar columnas created_at y updated_at de vehicle_types
    op.drop_column('brands', 'created_at')
    op.drop_column('brands', 'updated_at')
    op.drop_column('models', 'created_at')
    op.drop_column('models', 'updated_at')