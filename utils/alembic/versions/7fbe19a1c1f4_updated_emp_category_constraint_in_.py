"""Updated emp_category constraint in ContractEmployee

Revision ID: 7fbe19a1c1f4
Revises: a509134a825d
Create Date: 2024-03-14 09:08:17.476329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fbe19a1c1f4'
down_revision: Union[str, None] = 'a509134a825d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
