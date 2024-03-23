from data_model_flask_alchemy import Contract, User, ContractEmployee, ManpowerWage, Department, db

from all_flask_alchemy import app

import csv
from datetime import datetime


if __name__ == "__main__":

    with app.app_context():
#         department = Department(dept_no=25,dept_name="FNNP-25",dept_phone_no=2874)
#         db.session.add(department)
#         db.session.commit()
#         print("department added")
        #employees = db.session.query(ManpowerWage).filter(ContractEmployee.emp_name.in_(["NITYA SUNDAR MUDULI","JAGANNATH SAHU"])).all()
        # Assuming you have defined the Contract and ContractNew models

        with open('instance/departments.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
    
    # Iterate over each row in the CSV file
            for row in reader:
                # Convert date string to datetime object
                # Convert date string to datetime object
                department = Department(
                    dept_no=int(row['dept_no']),
                    dept_name=row['dept_name'],
                    dept_phone_no=int(row['dept_phone_no'])
                )
                
                # Add the new instance to the session
                db.session.add(department)
                    
                # Add the new instance to the session
                

    # Commit the session to persist the changes
        db.session.commit()

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






