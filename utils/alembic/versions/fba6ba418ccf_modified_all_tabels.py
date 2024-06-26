"""modified all tabels

Revision ID: fba6ba418ccf
Revises: 09f7a44e2158
Create Date: 2024-03-20 19:58:28.574092

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fba6ba418ccf'
down_revision: Union[str, None] = '09f7a44e2158'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('department',
    sa.Column('dept_no', sa.Integer(), nullable=False),
    sa.Column('dept_name', sa.String(), nullable=False),
    sa.Column('dept_phone_no', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('dept_no')
    )
    op.create_table('labour_wages',
    sa.Column('emp_category', sa.String(), nullable=False),
    sa.Column('wage', sa.Numeric(precision=6, scale=2), nullable=False),
    sa.CheckConstraint("emp_category IN ('skilled','semi-skilled','unskilled')"),
    sa.PrimaryKeyConstraint('emp_category')
    )
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('password_hash', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('contracts',
    sa.Column('contract_no', sa.String(), nullable=False),
    sa.Column('eic_pbno', sa.String(), nullable=True),
    sa.Column('oic_pbno', sa.String(), nullable=True),
    sa.Column('contract_type', sa.String(), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('duration_months', sa.Integer(), nullable=True),
    sa.Column('bill_frequency', sa.Integer(), nullable=True),
    sa.Column('contract_value', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('contract_description', sa.String(), nullable=False),
    sa.Column('vendor_id', sa.String(), nullable=False),
    sa.Column('vendor_name', sa.String(), nullable=False),
    sa.Column('vendor_address', sa.String(), nullable=False),
    sa.Column('vendor_gst', sa.String(), nullable=False),
    sa.Column('eic_dept_no', sa.String(), nullable=False),
    sa.Column('work_order_no', sa.String(), nullable=False),
    sa.Column('gem_contract_no', sa.String(), nullable=False),
    sa.CheckConstraint("contract_type IN ('manpower', 'work_package')"),
    sa.ForeignKeyConstraint(['eic_dept_no'], ['department.dept_no'], ),
    sa.PrimaryKeyConstraint('contract_no'),
    sa.UniqueConstraint('contract_no')
    )
    op.create_table('bills',
    sa.Column('ge_no', sa.Integer(), nullable=False),
    sa.Column('contract_no', sa.String(), nullable=True),
    sa.Column('rar_no', sa.Integer(), nullable=True),
    sa.Column('invoice_no', sa.String(), nullable=True),
    sa.Column('invoice_date', sa.Date(), nullable=True),
    sa.Column('invoice_amount', sa.Integer(), nullable=True),
    sa.Column('ge_date', sa.Date(), nullable=True),
    sa.Column('rr_no', sa.String(), nullable=True),
    sa.Column('penalty', sa.Integer(), nullable=True),
    sa.Column('abstract_timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['contract_no'], ['contracts.contract_no'], ),
    sa.PrimaryKeyConstraint('ge_no'),
    sa.UniqueConstraint('invoice_no'),
    sa.UniqueConstraint('rr_no')
    )
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
    op.drop_table('bills')
    op.drop_table('contracts')
    op.drop_table('users')
    op.drop_table('labour_wages')
    op.drop_table('department')
    # ### end Alembic commands ###
