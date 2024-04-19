from data_model_flask_alchemy import db
from sqlalchemy.exc import SQLAlchemyError

from data_model_flask_alchemy import BillsBoqLines,ContractBills
from sqlalchemy import and_


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


def check_values_exists_in_bills_table(session):
    print(session["checklist_data"])

    # conditions = and_(
    #                     ContractBills.contract_no != session["checklist_data"].get("contract_no"),
    #                     # ContractBills.ge_no == session["checklist_data"].get("ge_no"),
    #                     # ContractBills.rr_no == session["checklist_data"].get("rr_no")
    #                 )
    
    results = db.session.query(ContractBills).filter(ContractBills.contract_no != session["checklist_data"].get("contract_no")).all()
    print(results)

    for result in results:
        # print(result.ge_no,session["checklist_data"].get("ge_no"))
        if result.ge_no == session["checklist_data"].get("ge_number"):
            return f"Entered Gate Entry No already exists with Contract No:{result.contract_no},RAR NO:{result.rar_no}"
        elif result.rr_no == session["checklist_data"].get("rr_no"):
            return f"Entered RR No already exists with Contract No:{result.contract_no},RAR NO:{result.rar_no}"
    else:
        return False
    
def check_invoice_in_bills_tables(session):
    results = db.session.query(ContractBills).filter(ContractBills.contract_no != session["rar_abstract_data"].get("contract_no")).all()
    for result in results:
        # print(result.ge_no,session["checklist_data"].get("ge_no"))
        if result.invoice_no == session["rar_abstract_data"].get("invoice_no"):
            return f"Entered INVOICE No already exists with Contract No:{result.contract_no},RAR NO:{result.rar_no}"
        
    else:
        return False
