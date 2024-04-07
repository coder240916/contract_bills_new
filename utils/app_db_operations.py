from data_model_flask_alchemy import db
from sqlalchemy.exc import SQLAlchemyError

from data_model_flask_alchemy import BillsBoqLines,ContractBills


# Function to insert or update a record based on primary keys
def insert_or_update_bills_boq_lines(contract_no, boq_line_no, rar_no, qty):
    try:
        record = BillsBoqLines.query.filter_by(contract_no=contract_no, boq_line_no=boq_line_no, rar_no=rar_no).first()
        if record:
            # Update existing record
            record.qty = qty
            db.session.commit()
            return "data updated successfully in BillsBoqLines table."
        else:
            # Insert new record
            new_record = BillsBoqLines(contract_no=contract_no, boq_line_no=boq_line_no, rar_no=rar_no, qty=qty)
            db.session.add(new_record)
            db.session.commit()
            return "data inserted successfully into  BillsBoqLines table."

          # Indicates success
    except SQLAlchemyError as e:
        db.session.rollback()
        return f"Error occurred: {str(e)}"  # Indicates failure
    

# Function to insert or update a record based on primary keys
def insert_or_update_contract_bill(ge_no, contract_no, rar_no, invoice_no, invoice_date, invoice_amount, ge_date, rr_no, penalty, from_date, to_date, bill_payment_date):
    try:
        record = ContractBills.query.filter_by(contract_no=contract_no, rar_no=rar_no).first()
        if record:
            # Update existing record
            record.ge_no = ge_no
            record.invoice_no = invoice_no
            record.invoice_date = invoice_date
            record.invoice_amount = invoice_amount
            record.ge_date = ge_date
            record.rr_no = rr_no
            record.penalty = penalty
            record.from_date = from_date
            record.to_date = to_date
            record.bill_payment_date = bill_payment_date
            db.session.commit()
            return "data updated successfully in bills table"
        else:
            # Insert new record
            new_record = ContractBills(ge_no=ge_no, contract_no=contract_no, rar_no=rar_no, invoice_no=invoice_no,
                                       invoice_date=invoice_date, invoice_amount=invoice_amount, ge_date=ge_date,
                                       rr_no=rr_no, penalty=penalty, from_date=from_date, to_date=to_date,
                                       bill_payment_date=bill_payment_date)
            db.session.add(new_record)
            db.session.commit()
            return "data inserted successfully into bills table"  # Indicates success
    except Exception as e:
        db.session.rollback()
        return f"Error occurred: {str(e)}"  # Indicates failure
