"""creacion tabla vehiculos

Revision ID: 2990eccb1195
Revises: 9f959d74bb5a
Create Date: 2024-10-02 10:56:24.531382

"""
from typing import Sequence, Union
from sqlalchemy.sql import func
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2990eccb1195'
down_revision: Union[str, None] = '9f959d74bb5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # Eliminar la tabla vehicles en caso de rollback
    op.drop_table('vehicles')



def downgrade() -> None:
    op.create_table(
        'vehicles',
        sa.Column('id', sa.Integer, primary_key=True, index=True, nullable=False),
        sa.Column('model_id', sa.Integer, sa.ForeignKey('models.id'), nullable=False),
        sa.Column('vehicle_type_id', sa.Integer, sa.ForeignKey('vehicle_types.id'), nullable=False),
        sa.Column('vin', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False),
    )