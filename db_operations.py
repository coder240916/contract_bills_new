from data_model_flask_alchemy import Contract, User, ContractEmployee, ManpowerWage, Department, db, BillOfQuantities
from sqlalchemy import and_,distinct

from app import app

import csv
from datetime import datetime


if __name__ == "__main__":

    with app.app_context():
        contracts = db.session.query(Contract).all()
        print([contract.contract_no for contract in contracts])
         #boq_lines = BillOfQuantities.query.filter(BillOfQuantities.contract_no=="22SNSJO-373").order_by(BillOfQuantities.sl_no).all()
        #  boq_lines = db.session.query(BillOfQuantities).filter(BillOfQuantities.contract_no == "22SNCJO-373").all()
        #  print([[boq_line.sl_no,boq_line.description] for boq_line in boq_lines])
        # result = BillOfQuantities.query.filter( and_( 
        #                                               BillOfQuantities.description.ilike('%service charges%'), 
        #                                               BillOfQuantities.contract_no == contract_no)
        #                                               ).order_by(BillOfQuantities.sl_no).all()
                                                   
        # # Print the results
        # service_charges = []
        # for item in result:
        #     print(item.sl_no,item.description, item.qty, item.unit, item.rate, item.amount)
        #     service_charges.append(float(item.rate))

        # print(sorted(service_charges,reverse=True))
#         department = Department(dept_no=25,dept_name="FNNP-25",dept_phone_no=2874)
#         db.session.add(department)
#         db.session.commit()
#         print("department added")
        #employees = db.session.query(ManpowerWage).filter(ContractEmployee.emp_name.in_(["NITYA SUNDAR MUDULI","JAGANNATH SAHU"])).all()
        # Assuming you have defined the Contract and ContractNew models

    #     with open('instance/boq.csv', newline='') as csvfile:
    #         reader = csv.DictReader(csvfile)
    
    # # Iterate over each row in the CSV file
    #         for row in reader:
                
    #             # Add departments data
    #             # Convert date string to datetime object
    #             # department = Department(
    #             #     dept_no=int(row['dept_no']),
    #             #     dept_name=row['dept_name'],
    #             #     dept_phone_no=int(row['dept_phone_no'])
    #             # )
                
    #             # # Add the new instance to the session
    #             # db.session.add(department)
                    
    #             #  Add employees data
    #             # row['date_of_joining'] = datetime.strptime(row['date_of_joining'], '%Y-%m-%d')
        
    #             # # Create a new instance of ContractEmployee
    #             # contract_employee = ContractEmployee(
    #             #     emp_punch_id=int(row['emp_punch_id']),
    #             #     emp_name=row['emp_name'],
    #             #     contract_no=row['contract_no'],
    #             #     esi_no=int(row['esi_no']),
    #             #     pf_no=int(row['pf_no']),
    #             #     bank_acc_no=int(row['bank_acc_no']),
    #             #     date_of_joining=row['date_of_joining'],
    #             #     emp_category=row['emp_category'],
    #             #     bank_acc_ifsc_code=row['bank_acc_ifsc_code']
    #             # )
                
    #             # # Add the new instance to the session
    #             # db.session.add(contract_employee)

    #             # Add contracts data
    #             # Convert date string to datetime object
    #             # row['start_date'] = datetime.strptime(row['start_date'], '%Y-%m-%d')
                
    #             # # Create a new instance of ContractNew
    #             # contract_new = Contract(
    #             #     contract_no=row['contract_no'],
    #             #     eic_pbno=row['eic_pbno'],
    #             #     oic_pbno=row['oic_pbno'],
    #             #     contract_type=row['contract_type'],
    #             #     start_date=row['start_date'],
    #             #     duration_months=int(row['duration_months']),
    #             #     bill_frequency=int(row['bill_frequency']),
    #             #     contract_value=float(row['contract_value']),
    #             #     contract_description=row['contract_description'],
    #             #     vendor_id=row['vendor_id'],
    #             #     vendor_name=row['vendor_name'],
    #             #     vendor_address=row['vendor_address'],
    #             #     vendor_gst=row['vendor_gst'],
    #             #     eic_dept_no=int(row['eic_dept_no']),
    #             #     work_order_no=row['work_order_no'],
    #             #     gem_contract_no=row['gem_contract_no']
    #             # )
                
    #             # # Add the new instance to the session
    #             # db.session.add(contract_new)


                
    #             # Create a new instance of BillOfQuantities
    #             bill_of_quantity = BillOfQuantities(
    #                 sl_no=int(row['SL NO.']),
    #                 contract_no = row["CONTRACT_NO"],
    #                 description=row['DESCRIPTION'],
    #                 qty=float(row['QTY']),
    #                 unit=row['UNIT'],
    #                 rate=float(row['RATE']),
    #                 amount=float(row['AMOUNT'])
    #             )
                
    #             # Add the new instance to the session
    #             db.session.add(bill_of_quantity)
                        

    # # Commit the session to persist the changes
    #     db.session.commit()

        # db.reflect()
        #
        # for table_name in db.metadata.tables.keys():
        #     print(table_name)
        #
        #
        # result = db.session.query(db.metadata.tables["users"]).all()
        #
        #
        # for row in result:
        #     print(row)

        # user = db.session.query(User).filter_by(username="9216").first()
        # db.session.delete(user)
        # db.session.commit()

        #db.metadata.tables["alembic_version"].drop(db.engine)






