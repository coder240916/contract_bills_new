"""updated ContractBills

Revision ID: 005b38dfd067
Revises: 6bdd3c238de8
Create Date: 2024-04-07 22:26:05.803367

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005b38dfd067'
down_revision: Union[str, None] = '6bdd3c238de8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bills', sa.Column('bill_payment_date', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bills', 'bill_payment_date')
    # ### end Alembic commands ###
