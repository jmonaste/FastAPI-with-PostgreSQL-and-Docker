"""table names remaned

Revision ID: 6975310891a4
Revises: d8d2c76edc87
Create Date: 2024-10-01 16:29:21.598666

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6975310891a4'
down_revision: Union[str, None] = 'd8d2c76edc87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Renombrar tablas
    op.rename_table('brands', 'brand')
    op.rename_table('models', 'model')
    op.rename_table('vehicle_types', 'vehicle_type')


def downgrade() -> None:
    # Renombrar tablas
    op.rename_table('brand', 'brands')
    op.rename_table('model', 'models')
    op.rename_table('vehicle_type', 'vehicle_types')
