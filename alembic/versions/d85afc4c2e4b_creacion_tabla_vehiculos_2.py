"""creacion tabla vehiculos 2

Revision ID: d85afc4c2e4b
Revises: 2990eccb1195
Create Date: 2024-10-02 10:59:15.989439

"""
from typing import Sequence, Union
from sqlalchemy.sql import func
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd85afc4c2e4b'
down_revision: Union[str, None] = '2990eccb1195'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'vehicles',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('model_id', sa.Integer(), sa.ForeignKey('models.id'), nullable=False),
        sa.Column('vehicle_type_id', sa.Integer(), sa.ForeignKey('vehicle_types.id'), nullable=False),
        sa.Column('vin', sa.String(), nullable=False, unique=True, index=True),  # VIN debe ser único
        sa.Column('created_at', sa.DateTime(), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False),
    )

    # Crear índices adicionales si es necesario (opcional, Alembic puede manejarlo automáticamente con `index=True`)
    #op.create_index(op.f('ix_vehicles_id'), 'vehicles', ['id'])
    #op.create_index(op.f('ix_vehicles_vin'), 'vehicles', ['vin'])


def downgrade() -> None:
    # Eliminar los índices primero si los creaste manualmente
    #op.drop_index(op.f('ix_vehicles_vin'), table_name='vehicles')
    #op.drop_index(op.f('ix_vehicles_id'), table_name='vehicles')

    # Luego, elimina la tabla
    op.drop_table('vehicles')