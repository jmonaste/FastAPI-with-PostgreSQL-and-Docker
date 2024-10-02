"""actualizacion campo model_id por vehicle_model_id

Revision ID: 149af760563e
Revises: d85afc4c2e4b
Create Date: 2024-10-02 14:12:36.366654

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '149af760563e'
down_revision: Union[str, None] = 'd85afc4c2e4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Renombrar la columna model_id a vehicle_model_id
    op.alter_column('vehicles', 'model_id', new_column_name='vehicle_model_id')


def downgrade() -> None:
    # Volver a renombrar la columna vehicle_model_id a model_id
    op.alter_column('vehicles', 'vehicle_model_id', new_column_name='model_id')