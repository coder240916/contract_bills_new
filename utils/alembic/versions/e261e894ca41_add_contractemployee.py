"""Add ContractEmployee

Revision ID: e261e894ca41
Revises: 18af43bcdedf
Create Date: 2024-03-14 09:22:23.195758

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e261e894ca41'
down_revision: Union[str, None] = '18af43bcdedf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contract_employees',
    sa.Column('emp_punch_id', sa.Integer(), nullable=False),
    sa.Column('emp_name', sa.String(), nullable=True),
    sa.Column('contract_no', sa.String(), nullable=True),
    sa.Column('esi_no', sa.Integer(), nullable=True),
    sa.Column('pf_no', sa.Integer(), nullable=True),
    sa.Column('bank_acc_no', sa.Integer(), nullable=True),
    sa.Column('date_of_joining', sa.Date(), nullable=True),
    sa.Column('emp_category', sa.String(), nullable=True),
    sa.Column('bank_acc_ifsc_code', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['contract_no'], ['contracts.contract_no'], ),
    sa.PrimaryKeyConstraint('emp_punch_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('contract_employees')
    # ### end Alembic commands ###
