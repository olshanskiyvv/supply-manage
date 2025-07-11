"""Update user model

Revision ID: a054d3f01943
Revises: d18a954a990d
Create Date: 2025-05-06 15:10:08.259071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a054d3f01943'
down_revision: Union[str, None] = 'd18a954a990d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'patronymic',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'patronymic',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
