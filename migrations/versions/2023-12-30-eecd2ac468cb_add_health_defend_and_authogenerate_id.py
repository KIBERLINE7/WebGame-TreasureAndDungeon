"""Add Health, Defend and authogenerate ID

Revision ID: eecd2ac468cb
Revises: 17bb0b46a25d
Create Date: 2023-12-30 23:00:04.597897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eecd2ac468cb'
down_revision: Union[str, None] = '17bb0b46a25d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('character', sa.Column('health', sa.Integer(), nullable=False))
    op.add_column('character', sa.Column('attack_point', sa.Integer(), nullable=False))
    op.add_column('character', sa.Column('defend', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('character', 'defend')
    op.drop_column('character', 'attack_point')
    op.drop_column('character', 'health')
    # ### end Alembic commands ###
