"""added boq tbale

Revision ID: 76f922b9ff6a
Revises: 52ae9b1bd504
Create Date: 2024-03-23 16:24:59.240579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76f922b9ff6a'
down_revision: Union[str, None] = '52ae9b1bd504'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bill_of_quantities',
    sa.Column('sl_no', sa.Integer(), nullable=False),
    sa.Column('contract_no', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('qty', sa.Integer(), nullable=True),
    sa.Column('unit', sa.String(), nullable=False),
    sa.Column('rate', sa.Integer(), nullable=True),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['contract_no'], ['contracts.contract_no'], ),
    sa.PrimaryKeyConstraint('sl_no')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bill_of_quantities')
    # ### end Alembic commands ###
