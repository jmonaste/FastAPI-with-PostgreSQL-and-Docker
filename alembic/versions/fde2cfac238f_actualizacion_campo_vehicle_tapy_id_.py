"""actualizacion campo vehicle_tapy_id - renombrar

Revision ID: fde2cfac238f
Revises: 149af760563e
Create Date: 2024-10-02 14:18:34.214473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fde2cfac238f'
down_revision: Union[str, None] = '149af760563e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Renombrar la columna model_id a vehicle_model_id
    op.alter_column('vehicles', 'vehicle_type_id', new_column_name='type_id')


def downgrade() -> None:
    # Volver a renombrar la columna vehicle_model_id a model_id
    op.alter_column('vehicles', 'type_id', new_column_name='vehicle_type_id')