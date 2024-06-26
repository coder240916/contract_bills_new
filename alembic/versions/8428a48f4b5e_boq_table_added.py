"""boq table added

Revision ID: 8428a48f4b5e
Revises: a8e5760de78e
Create Date: 2024-03-24 08:36:06.769044

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8428a48f4b5e'
down_revision: Union[str, None] = 'a8e5760de78e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bill_of_quantities',
    sa.Column('sl_no', sa.Integer(), nullable=False),
    sa.Column('contract_no', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('qty', sa.Integer(), nullable=False),
    sa.Column('unit', sa.String(), nullable=False),
    sa.Column('rate', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['contract_no'], ['contracts.contract_no'], ),
    sa.PrimaryKeyConstraint('sl_no', 'contract_no')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bill_of_quantities')
    # ### end Alembic commands ###
