"""boq table deleted

Revision ID: a8e5760de78e
Revises: 668d7bf41843
Create Date: 2024-03-24 08:35:48.128866

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8e5760de78e'
down_revision: Union[str, None] = '668d7bf41843'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bill_of_quantities')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bill_of_quantities',
    sa.Column('sl_no', sa.INTEGER(), nullable=False),
    sa.Column('contract_no', sa.VARCHAR(), nullable=False),
    sa.Column('description', sa.VARCHAR(), nullable=False),
    sa.Column('qty', sa.INTEGER(), nullable=True),
    sa.Column('unit', sa.VARCHAR(), nullable=False),
    sa.Column('rate', sa.INTEGER(), nullable=True),
    sa.Column('amount', sa.NUMERIC(precision=10, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['contract_no'], ['contracts.contract_no'], ),
    sa.PrimaryKeyConstraint('sl_no', 'contract_no')
    )
    # ### end Alembic commands ###
