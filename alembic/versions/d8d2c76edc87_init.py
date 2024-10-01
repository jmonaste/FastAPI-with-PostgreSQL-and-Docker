"""Init

Revision ID: d8d2c76edc87
Revises: 
Create Date: 2024-10-01 16:18:36.638122

"""
from typing import Sequence, Union
from sqlalchemy import func
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8d2c76edc87'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear la tabla 'brands'
    op.create_table(
        'brands',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, unique=True, index=True),
        sa.Column('created_at', sa.DateTime, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Crear la tabla 'models'
    op.create_table(
        'models',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, index=True),
        sa.Column('brand_id', sa.Integer, sa.ForeignKey('brands.id')),
        sa.Column('created_at', sa.DateTime, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Crear la tabla 'vehicle_types'
    op.create_table(
        'vehicle_types',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('type_name', sa.String, unique=True, index=True),
        sa.Column('created_at', sa.DateTime, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=func.now(), onupdate=func.now())
    )


def downgrade() -> None:
    # Eliminar la tabla 'models'
    op.drop_table('models')

    # Eliminar la tabla 'brands'
    op.drop_table('brands')

    # Eliminar la tabla 'vehicle_types'
    op.drop_table('vehicle_types')
