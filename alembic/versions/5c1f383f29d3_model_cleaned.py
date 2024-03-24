"""model cleaned

Revision ID: 5c1f383f29d3
Revises: 76f922b9ff6a
Create Date: 2024-03-24 07:44:15.430033

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c1f383f29d3'
down_revision: Union[str, None] = '76f922b9ff6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('vendors')
    op.drop_table('labour_wages')
    op.drop_table('department')
    op.drop_table('bill_of_quantities')
    op.drop_table('users')
    op.drop_table('contracts')
    op.drop_table('bills')
    op.drop_table('contract_employees')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contract_employees',
    sa.Column('emp_punch_id', sa.INTEGER(), nullable=False),
    sa.Column('emp_name', sa.VARCHAR(), nullable=True),
    sa.Column('contract_no', sa.VARCHAR(), nullable=True),
    sa.Column('esi_no', sa.INTEGER(), nullable=True),
    sa.Column('pf_no', sa.INTEGER(), nullable=True),
    sa.Column('bank_acc_no', sa.INTEGER(), nullable=True),
    sa.Column('date_of_joining', sa.DATE(), nullable=True),
    sa.Column('emp_category', sa.VARCHAR(), nullable=True),
    sa.Column('bank_acc_ifsc_code', sa.VARCHAR(), nullable=True),
    sa.ForeignKeyConstraint(['contract_no'], ['contracts.contract_no'], ),
    sa.PrimaryKeyConstraint('emp_punch_id')
    )
    op.create_table('bills',
    sa.Column('ge_no', sa.INTEGER(), nullable=False),
    sa.Column('contract_no', sa.VARCHAR(), nullable=True),
    sa.Column('rar_no', sa.INTEGER(), nullable=True),
    sa.Column('invoice_no', sa.VARCHAR(), nullable=True),
    sa.Column('invoice_date', sa.DATE(), nullable=True),
    sa.Column('invoice_amount', sa.INTEGER(), nullable=True),
    sa.Column('ge_date', sa.DATE(), nullable=True),
    sa.Column('rr_no', sa.VARCHAR(), nullable=True),
    sa.Column('penalty', sa.INTEGER(), nullable=True),
    sa.Column('abstract_timestamp', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['contract_no'], ['contracts.contract_no'], ),
    sa.PrimaryKeyConstraint('ge_no'),
    sa.UniqueConstraint('invoice_no'),
    sa.UniqueConstraint('rr_no')
    )
    op.create_table('contracts',
    sa.Column('contract_no', sa.VARCHAR(), nullable=False),
    sa.Column('eic_pbno', sa.VARCHAR(), nullable=True),
    sa.Column('oic_pbno', sa.VARCHAR(), nullable=True),
    sa.Column('contract_type', sa.VARCHAR(), nullable=True),
    sa.Column('start_date', sa.DATE(), nullable=True),
    sa.Column('duration_months', sa.INTEGER(), nullable=True),
    sa.Column('bill_frequency', sa.INTEGER(), nullable=True),
    sa.Column('contract_value', sa.NUMERIC(precision=10, scale=2), nullable=False),
    sa.Column('contract_description', sa.VARCHAR(), nullable=False),
    sa.Column('vendor_id', sa.VARCHAR(), nullable=False),
    sa.Column('vendor_name', sa.VARCHAR(), nullable=False),
    sa.Column('vendor_address', sa.VARCHAR(), nullable=False),
    sa.Column('vendor_gst', sa.VARCHAR(), nullable=False),
    sa.Column('eic_dept_no', sa.VARCHAR(), nullable=False),
    sa.Column('work_order_no', sa.VARCHAR(), nullable=False),
    sa.Column('gem_contract_no', sa.VARCHAR(), nullable=False),
    sa.CheckConstraint("contract_type IN ('manpower', 'work_package')"),
    sa.ForeignKeyConstraint(['eic_dept_no'], ['department.dept_no'], ),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendors.vendor_id'], ),
    sa.PrimaryKeyConstraint('contract_no'),
    sa.UniqueConstraint('contract_no')
    )
    op.create_table('users',
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(), nullable=True),
    sa.Column('password_hash', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('bill_of_quantities',
    sa.Column('sl_no', sa.INTEGER(), nullable=False),
    sa.Column('contract_no', sa.VARCHAR(), nullable=True),
    sa.Column('description', sa.VARCHAR(), nullable=False),
    sa.Column('qty', sa.INTEGER(), nullable=True),
    sa.Column('unit', sa.VARCHAR(), nullable=False),
    sa.Column('rate', sa.INTEGER(), nullable=True),
    sa.Column('amount', sa.NUMERIC(precision=10, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['contract_no'], ['contracts.contract_no'], ),
    sa.PrimaryKeyConstraint('sl_no')
    )
    op.create_table('department',
    sa.Column('dept_no', sa.INTEGER(), nullable=False),
    sa.Column('dept_name', sa.VARCHAR(), nullable=False),
    sa.Column('dept_phone_no', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('dept_no')
    )
    op.create_table('labour_wages',
    sa.Column('emp_category', sa.VARCHAR(), nullable=False),
    sa.Column('wage', sa.NUMERIC(precision=6, scale=2), nullable=False),
    sa.CheckConstraint("emp_category IN ('skilled','semi-skilled','unskilled')"),
    sa.PrimaryKeyConstraint('emp_category')
    )
    op.create_table('vendors',
    sa.Column('vendor_id', sa.VARCHAR(), nullable=False),
    sa.Column('vendor_epf_code', sa.VARCHAR(), nullable=False),
    sa.Column('vendor_esi_code', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('vendor_id')
    )
    # ### end Alembic commands ###
