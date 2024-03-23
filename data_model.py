from sqlalchemy import Column, Integer, String, ForeignKey, Date, CheckConstraint, DateTime, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship,sessionmaker,declarative_base
# from sqlalchemy.ext.declarative import declarative_base

# Create an engine and create the tables
# Replace 'your_database_url' with your actual database URL
from sqlalchemy import create_engine
engine = create_engine('sqlite:///contract_bills.db')

# Create a session
DBSession = sessionmaker(bind=engine)
db_session = DBSession()


# Define the new data model
Base = declarative_base()

Base.metadata.bind = engine

# Base = declarative_base()

class Contract(Base):
    __tablename__ = 'contracts'

    contract_no = Column(String, primary_key=True, unique=True)
    eic_pbno = Column(String)
    oic_pbno = Column(String)
    contract_type = Column(String)
    start_date = Column(Date)
    duration_months = Column(Integer)
    bill_frequency = Column(Integer, CheckConstraint('bill_frequency IN (1, 3)'))  # CheckConstraint for bill_frequency
    contract_value = Column(Numeric(precision=10,scale=2),nullable=False)
    contract_description = Column(String,nullable=False)
    vendor_id = Column(String,nullable=False)
    vendor_name = Column(String,nullable=False)
    vendor_address = Column(String,nullable=False)
    vendor_gst = Column(String,nullable=False)
    

    __table_args__ = (
        CheckConstraint("contract_type IN ('manpower', 'work_package')"),  # CheckConstraint for contract_type
    )

    # Define one-to-many relationship with ContractEmployees
    employees = relationship("ContractEmployee", back_populates="contract")
    bills = relationship("ContractBills",back_populates="contract")

    def __repr__(self):
        return f"<Contract {self.contract_no} {self.eic_pbno} {self.oic_pbno} {self.contract_type} {self.start_date} {self.duration_months} {self.bill_frequency}>"


class ContractEmployee(Base):
    __tablename__ = 'contract_employees'

    emp_punch_id = Column(Integer, primary_key=True)
    emp_name = Column(String)
    contract_no = Column(String, ForeignKey('contracts.contract_no'))
    esi_no = Column(Integer)
    pf_no = Column(Integer)
    bank_acc_no = Column(Integer)
    date_of_joining = Column(Date)
    emp_category = Column(String,CheckConstraint('emp_category IN ("skilled","semi-skilled","unskilled")'))
    bank_acc_ifsc_code = Column(String)

    # Define many-to-one relationship with Contract
    contract = relationship("Contract", back_populates="employees")


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String)


class ContractBills(Base):
    __tablename__ = 'bills'

    
    ge_no = Column(Integer,primary_key=True)
    contract_no = Column(String, ForeignKey('contracts.contract_no'))
    rar_no = Column(Integer)
    invoice_no = Column(String,unique=True)
    invoice_date = Column(Date)
    invoice_amount = Column(Integer)
    ge_date = Column(Date)
    rr_no = Column(String,unique=True)
    penalty = Column(Integer)
    abstract_timestamp = Column(DateTime, default=func.now()) 

    
    # Define many-to-one relationship with Contract
    contract = relationship("Contract", back_populates="bills")

    def __repr__(self):
        return f"<Bill(rar_no={self.rar_no}, contract_no = {self.contract_no}, invoice_no={self.invoice_no}), ge_no = {self.ge_no} , rr_no={self.rr_no} >"


class ManpowerWage(Base):
    __tablename__ = "labour_wages"

    # sl_no = Column(Integer, primary_key=True)
    emp_category = Column(String,primary_key=True)
    wage = Column(Numeric(precision=6,scale=2),nullable=False)

    __table_args__ = (
        CheckConstraint("emp_category IN ('skilled','semi-skilled','unskilled')"),  # CheckConstraint for contract_type
    )

    def __repr__(self):
        return f"<ManpowerWage(emp_category={self.emp_category}, wage = {self.wage}) >"




if __name__ == "__main__":
    Base.metadata.create_all(engine)
    #Base.metadata.create_all(engine, checkfirst=True)
    contract = db_session.query(Contract).filter(
                    (Contract.eic_pbno == '9216') | (Contract.oic_pbno == '9216')
                ).first()
    print(contract.oic_pbno)

