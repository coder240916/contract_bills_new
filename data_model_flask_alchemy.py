from sqlalchemy import Column, Integer, String, ForeignKey, Date, CheckConstraint, DateTime, Numeric,Float
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Contract(db.Model):
    __tablename__ = 'contracts'

    contract_no = db.Column(db.String, primary_key=True, unique=True)
    eic_pbno = db.Column(db.String)
    oic_pbno = db.Column(db.String)
    contract_type = db.Column(db.String)
    start_date = db.Column(db.Date)
    duration_months = db.Column(db.Integer)
    bill_frequency = db.Column(db.Integer, CheckConstraint('bill_frequency IN (1, 3)'))
    contract_value = db.Column(db.Numeric(precision=10,scale=2), nullable=False)
    contract_description = db.Column(db.String, nullable=False)
    vendor_id = db.Column(db.String, db.ForeignKey('vendors.vendor_id'),nullable=False)
    vendor_name = db.Column(db.String, nullable=False)
    vendor_address = db.Column(db.String, nullable=False)
    vendor_gst = db.Column(db.String, nullable=False)
    eic_dept_no = db.Column(db.String,db.ForeignKey('department.dept_no'),nullable=False,default=" ")
    work_order_no = db.Column(db.String,nullable=False)
    gem_contract_no = db.Column(db.String, nullable=False)

    __table_args__ = (
        CheckConstraint("contract_type IN ('manpower', 'work_package')"),
    )

    employees = db.relationship("ContractEmployee", back_populates="contract")
    bills = db.relationship("ContractBills", back_populates="contract")
    department = db.relationship("Department", back_populates="contract")
    vendor = db.relationship("Vendors", back_populates="contract")
    boq = db.relationship("BillOfQuantities", back_populates="contract")
    bills_boq_lines = db.relationship("BillsBoqLines", back_populates="contract")

    def __repr__(self):
        return f"<Contract {self.contract_no} {self.eic_pbno} {self.oic_pbno} {self.contract_type} {self.start_date} {self.duration_months} {self.bill_frequency}>"

class ContractEmployee(db.Model):
    __tablename__ = 'contract_employees'

    emp_punch_id = db.Column(db.Integer, primary_key=True)
    emp_name = db.Column(db.String)
    contract_no = db.Column(db.String, db.ForeignKey('contracts.contract_no'))
    esi_no = db.Column(db.Integer)
    pf_no = db.Column(db.Integer)
    bank_acc_no = db.Column(db.Integer)
    date_of_joining = db.Column(db.Date)
    emp_category = db.Column(db.String, CheckConstraint('emp_category IN ("skilled","semi-skilled","unskilled")'))
    bank_acc_ifsc_code = db.Column(db.String)
    aadhaar_no = db.Column(db.Integer)

    contract = db.relationship("Contract", back_populates="employees")

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)
    

class ManpowerWage(db.Model):
    __tablename__ = "labour_wages"

    emp_category = db.Column(db.String, primary_key=True)
    wage = db.Column(db.Numeric(precision=6, scale=2), nullable=False)

    __table_args__ = (
        CheckConstraint("emp_category IN ('skilled','semi-skilled','unskilled')"),
    )

    def __repr__(self):
        return f"<ManpowerWage(emp_category={self.emp_category}, wage = {self.wage})>"


class Department(db.Model):
    dept_no = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String, nullable=False)
    dept_phone_no = db.Column(db.Integer, nullable=False)

    contract = db.relationship("Contract", back_populates="department")

    
class Vendors(db.Model):
    __tablename__ = "vendors"

    vendor_id = db.Column(db.String, primary_key=True)
    vendor_epf_code = db.Column(db.String, nullable=False)
    vendor_esi_code = db.Column(db.String, nullable=False)

    contract = db.relationship("Contract", back_populates="vendor")

    
class BillOfQuantities(db.Model):
    __tablename__ = "bill_of_quantities"

    sl_no = db.Column(db.Integer, primary_key=True)
    contract_no = db.Column(db.String, db.ForeignKey('contracts.contract_no'),primary_key=True)
    description = db.Column(db.String, nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String,nullable=False)
    rate =  db.Column(db.Numeric(precision=10,scale=2), nullable=False)
    amount = db.Column(db.Numeric(precision=10,scale=2), nullable=False)

    contract = db.relationship("Contract", back_populates="boq")
    bills_boq_lines = db.relationship("BillsBoqLines",back_populates="boq")


class ContractBills(db.Model):
    __tablename__ = 'bills'

    ge_no = db.Column(db.Integer, unique=True)
    contract_no = db.Column(db.String, db.ForeignKey('contracts.contract_no'),primary_key=True)
    rar_no = db.Column(db.Integer,primary_key=True)
    invoice_no = db.Column(db.String, unique=True)
    invoice_date = db.Column(db.Date)
    invoice_amount = db.Column(db.Numeric(precision=10,scale=2), nullable=False)
    ge_date = db.Column(db.Date)
    rr_no = db.Column(db.String, unique=True)
    penalty = db.Column(db.Float)
    from_date = db.Column(db.Date)
    to_date = db.Column(db.Date)
    bill_timestamp = db.Column(db.DateTime, default=db.func.now())
    bill_payment_date = db.Column(db.Date,nullable=True)


    contract = db.relationship("Contract", back_populates="bills")

    def __repr__(self):
        return f"<Bill(rar_no={self.rar_no}, contract_no = {self.contract_no}, invoice_no={self.invoice_no}), ge_no = {self.ge_no} , rr_no={self.rr_no} >"


class BillsBoqLines(db.Model):
    __table_name__ = "bills_boq_lines"

    contract_no = db.Column(db.String, db.ForeignKey('contracts.contract_no'),primary_key=True)
    boq_line_no = db.Column(db.Integer, db.ForeignKey('bill_of_quantities.sl_no'),primary_key=True)
    rar_no = db.Column(db.Integer,primary_key=True)
    qty = db.Column(db.Float,nullable=False)

    contract = db.relationship("Contract", back_populates="bills_boq_lines")
    boq = db.relationship("BillOfQuantities", back_populates="bills_boq_lines")

