import os
import calendar
# import pandas as pd
from datetime import datetime,date


from flask import Flask, render_template, request, redirect, url_for,session,flash,jsonify
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from data_model import Base, Contract, User, ContractEmployee, ManpowerWage
from werkzeug.security import generate_password_hash, check_password_hash

from utils.utils import generate_data,generate_abstract,BILLS_FOLDER_PATH,get_prev_months
from utils.utils import generate_attendance_data_df

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key
app.static_folder = 'static'

# Create an engine and bind it to the base


engine = create_engine('sqlite:///instance/contract_bills.db')
Base.metadata.bind = engine

# Create a session
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# Admin credentials
# Add admin user if not exists
admin_user = db_session.query(User).filter_by(username='admin').first()

if not admin_user:
    admin_password_hash = generate_password_hash('admin')
    db_session.add(User(username='admin', password_hash=admin_password_hash))
    db_session.commit()

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        
        # Check if the user is admin
        if username == 'admin':
            user = db_session.query(User).filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.username
                return redirect(url_for('view_contracts'))
            else:
                flash("Invalid username or password.", "error")
                return render_template('login.html')
        
        # For non-admin users, check both users and contracts table
        else:
            # Check if the user exists in the users table
            user = db_session.query(User).filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                # Check if the user exists in the contracts table with either eic_pbno or oic_pbno
                contract = db_session.query(Contract).filter(
                    (Contract.eic_pbno == username) | (Contract.oic_pbno == username)
                ).first()

                if contract.eic_pbno == username:
                    
                    session['eic_user_id'] = user.username
                    return redirect(url_for('eic_dashboard'))
                   

                elif contract.oic_pbno == username:
                    session['oic_user_id'] = user.username
                    return redirect(url_for('oic_dashboard'))

                else:
                    flash("You are not authorized to access the system.", "error")
                    return render_template('login.html')
            else:
                flash("Invalid username or password.", "error")
                return render_template('login.html')
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('login'))


# Dashboard route
@app.route('/eic_dashboard')
def eic_dashboard():
    if 'eic_user_id' not in session:
        return redirect(url_for('login'))
    
    contracts = db_session.query(Contract).filter( Contract.eic_pbno == session['eic_user_id'] ).all()
    return render_template('eic_dashboard.html',no_of_contracts=len(contracts))

# # Dashboard route
# @app.route('/eic_dashboard_manpower')
# def eic_dashboard_manpower():
#     if 'eic_user_id_manpower' not in session:
#         return redirect(url_for('login'))
    
#     contracts = db_session.query(Contract).filter(
#                     (Contract.eic_pbno == session['eic_user_id_manpower']) & (Contract.contract_type == session["dash_board_type"])
#                 ).all()
#     print(contracts)
#     return render_template('eic_dashboard_manpower.html',no_of_contracts=len(contracts))

# Dashboard route
@app.route('/oic_dashboard')
def oic_dashboard():
    if 'oic_user_id' not in session:
        return redirect(url_for('login'))
    return render_template('oic_dashboard.html')


# Contract routes
@app.route('/contracts')
def view_contracts():
    if session['user_id'] != 'admin':
        flash("You are not authorized to access this page.", "error")
        return redirect(url_for('login'))
    contracts = db_session.query(Contract).all()
    return render_template('view_contracts.html', contracts=contracts)

# User routes
@app.route('/users')
def view_users():
    if session['user_id'] != 'admin':
        flash("You are not authorized to access this page.", "error")
        return redirect(url_for('login'))
    users = db_session.query(User).all()
    return render_template('view_users.html', users=users)


# Contract form route
@app.route('/add_contract', methods=['POST'])
def add_contract():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        contract_no = request.form['contract_no']
        eic_pbno = int(request.form['eic_pbno'])
        oic_pbno = int(request.form['oic_pbno'])
        contract_type = request.form['contract_type']
        start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        duration_months = request.form["duration_months"]
        bill_frequency = request.form["bill_frequency"]
        contract_value = request.form["contract_value"]
        contract_description = request.form["contract_description"]
        vendor_id = request.form["vendor_id"]
        vendor_name = request.form["vendor_name"]
        vendor_address = request.form["vendor_address"]
        vendor_gst = request.form["vendor_gst"]
        
        new_contract = Contract(contract_no=contract_no, eic_pbno=eic_pbno, oic_pbno=oic_pbno, contract_type=contract_type, 
                                start_date=start_date,duration_months = duration_months,bill_frequency = bill_frequency,contract_value=contract_value,
                                contract_description = contract_description,vendor_id=vendor_id,vendor_name=vendor_name,
                                vendor_address = vendor_address,vendor_gst=vendor_gst)
        
        db_session.add(new_contract)
        db_session.commit()
        return redirect(url_for('view_contracts'))
    return redirect(url_for('view_contracts'))


@app.route('/delete_contract/<contract_no>', methods=['POST'])
def delete_contract(contract_no):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    contract = db_session.query(Contract).filter_by(contract_no=contract_no).first()
    if contract:
        db_session.delete(contract)
        db_session.commit()
    return redirect(url_for('view_contracts'))


@app.route('/update_contract/<contract_no>', methods=['POST'])
def update_contract(contract_no):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    eic_pbno_update = int(request.form['eic_pbno_update'])
    oic_pbno_update = int(request.form['oic_pbno_update'])

    contract = db_session.query(Contract).filter_by(contract_no=contract_no).first()
    if contract:
        contract.eic_pbno = eic_pbno_update
        contract.oic_pbno = oic_pbno_update
        db_session.commit()
    return redirect(url_for('view_contracts'))


# Add User route
@app.route('/add_user', methods=['POST'])
def add_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    username = request.form['username']
    password = request.form['password']
    
    # Check if the username already exists
    existing_user = db_session.query(User).filter_by(username=username).first()
    if existing_user:
        flash("User with this username already exists.", "error")
        return redirect(url_for('view_users'))

    # Hash the password
    password_hash = generate_password_hash(password)
    
    # Create a new user
    new_user = User(username=username, password_hash=password_hash)
    db_session.add(new_user)
    db_session.commit()
    
    return redirect(url_for('view_users'))

# Delete User route
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Query the user by user_id
    user_to_delete = db_session.query(User).filter_by(user_id=user_id).first()
    
    # Check if the user exists
    if not user_to_delete:
        flash("User Not found", "error")
        return redirect(url_for('view_users'))
    
    # Delete the user
    db_session.delete(user_to_delete)
    db_session.commit()
    
    return redirect(url_for('view_users'))

@app.route('/manpower')
def manpower():
    if 'user_id' in session or "eic_user_id" not in session :
        return redirect(url_for('login'))
    contracts = db_session.query(Contract).filter_by(eic_pbno=session["eic_user_id"]).all()
    employees = db_session.query(ContractEmployee).filter_by(contract_no=contracts[0].contract_no).all()
    return render_template('manpower.html', contracts=contracts,employees=employees)



# Contract form route
@app.route('/add_manpower', methods=['POST'])
def add_manpower():
    if 'user_id' in session or "eic_user_id" not in session :
        return redirect(url_for('login'))

    if request.method == 'POST':
        punch_id = request.form['punch_id']
        emp_name = request.form['emp_name']
        contract_no = request.form['contract_no']
        esi_no = int(request.form['esi_no'])
        pf_no = int(request.form['pf_no'])
        bank_ac_no = int(request.form["bank_ac_no"])
        dt_of_join = datetime.strptime(request.form["dt_of_join"], "%Y-%m-%d").date()
        emp_category = request.form["emp_category"]
        bank_acc_ifsc_code = request.form["bank_acc_ifsc_code"]
        
        
        new_employee = ContractEmployee(emp_punch_id=punch_id, emp_name=emp_name, contract_no=contract_no, esi_no=esi_no, 
                                pf_no=pf_no,bank_acc_no = bank_ac_no,date_of_joining = dt_of_join,emp_category=emp_category,
                                bank_acc_ifsc_code = bank_acc_ifsc_code,)
        try:
            db_session.add(new_employee)
            db_session.commit()
        except SQLAlchemyError as e:
            db_session.rollback()
            error_message = str(e.orig)
            if 'UNIQUE constraint failed' in error_message:
                flash('Employee already exists.', 'error')
            else:
                flash('Error occurred while adding user: {}'.format(error_message), 'error')

        return redirect(url_for('manpower'))
    return redirect(url_for('manpower'))


@app.route('/delete_manpower/<emp_punch_id>', methods=['POST'])
def delete_manpower(emp_punch_id):
    if 'user_id' in session or "eic_user_id" not in session :
        return redirect(url_for('login'))
    
    employee = db_session.query(ContractEmployee).filter_by(emp_punch_id=emp_punch_id).first()
    if employee:
        db_session.delete(employee)
        db_session.commit()
    return redirect(url_for('manpower'))


@app.route('/update_manpower/<emp_punch_id>', methods=['POST'])
def update_manpower(emp_punch_id):
    if 'user_id' in session or "eic_user_id" not in session :
        return redirect(url_for('login'))

    emp_name_update = request.form['emp_name']
    contract_no_update = request.form['contract_no']

    employee = db_session.query(ContractEmployee).filter_by(emp_punch_id=emp_punch_id).first()
    contracts = db_session.query(Contract).filter_by( eic_pbno=session["eic_user_id"]).all()
    contract_nos = [contract.contract_no for contract in contracts]

    if contract_no_update not in contract_nos:
        flash("Invalid Contract No.Please enter valid contract no or contact admin", "error")
        return redirect(url_for('manpower'))


    if employee:
        employee.emp_name = emp_name_update
        employee.contract_no = contract_no_update
        db_session.commit()
    return redirect(url_for('manpower'))

# attendance endpoint
@app.route("/attendance",methods=["GET","POST"])
def attendance():
    if 'user_id' in session or "eic_user_id" not in session :
        return redirect(url_for('login'))
    
    month_dict = get_prev_months()

    contracts = db_session.query(Contract).filter(Contract.eic_pbno == session["eic_user_id"])

    if request.method == "POST":
        month,year = request.form["month_select"].split("-")
      
        contract_no = request.form["contract_select"]
        employees = db_session.query(ContractEmployee).filter_by(contract_no=contract_no).all()
        employees = [employee.emp_name for employee in employees]
        session["attendance_data"] = {"month":int(month),"year":int(year),"contract_no":contract_no,"employees":employees}

        attendance_data = generate_attendance_data_df(employees,int(month),int(year))
        return render_template("attendance_form.html",attendance_data=attendance_data,contracts=contracts,month_dict=month_dict)

    return render_template("attendance_form.html",contracts=contracts,month_dict=month_dict)


@app.route("/save_attendance",methods=["POST"])
def save_attendance():
    updated_attendance = request.form['attendance_data']
    month,year = session["attendance_data"].get("month"),session["attendance_data"].get("year")
    employees = session["attendance_data"].get("employees")
    contract_no = session["attendance_data"].get("contract_no")
    
    print(session["attendance_data"])

    # month_number = {name: num for num, name in enumerate(calendar.month_name) if num}
    
    num_days = calendar.monthrange(year=year, month=month)[1]
    attendance_dates = [f"{day:02d}/{month:02d}" for day in range(1, num_days + 1)]

    print(attendance_dates)
    print(employees)
    print(updated_attendance)
    return updated_attendance



# create bill for EIC users
@app.route("/create_bill",methods=["GET","POST"])
def create_bill():
    if 'user_id' in session or "eic_user_id" not in session :
        return redirect(url_for('login'))
    
    contracts = db_session.query(Contract).filter(Contract.eic_pbno == session["eic_user_id"])

    if request.method == "POST":
        contract_no = request.form['contract_no']
        rar_no = int(request.form['rar_no'])
        penalty = int(request.form['penalty'])
        invoice_no = request.form['invoice_no']
        invoice_date = str(datetime.strptime(request.form["invoice_date"], "%Y-%m-%d").date())
        invoice_amount = request.form["invoice_amount"]
        bill_abstract = request.form.get("bill_abstract")

        if bill_abstract:
            contract_folder_path = os.path.join(app.root_path,BILLS_FOLDER_PATH,f"{contract_no}",f"RAR_{rar_no}")
            rar_template_path = os.path.join(app.root_path,BILLS_FOLDER_PATH,f"{contract_no}","bill_templates","RAR.xlsx")
            

            os.makedirs(contract_folder_path,exist_ok=True)
            target_path = os.path.join(app.root_path,BILLS_FOLDER_PATH,f"{contract_no}",f"RAR_{rar_no}","bill_abstract.xlsx")
            # data = generate_data(rar_template_path,rar_no)
            # message = generate_abstract(data,rar_template_path,rar_no,penalty,target_path)
            flash("Bill Abstract generated successfully!","success")
            bill_data = {"contract_no":contract_no,"rar_no":rar_no,"penalty":penalty,
                        "invoice_no":invoice_no,"invoice_date":invoice_date,
                        "invoice_amount":invoice_amount,"abstract_date":str(datetime.now().strftime("%d-%m-%Y %H:%M")),
                        "bill_abstract":bill_abstract}
            session["bill_data"] = bill_data
            return render_template("create_bill.html",contracts=contracts,message="generate_ifs_bill")
        else:
            flash("please select the bill abstract checkbox","no-selection")
            return render_template("create_bill.html",contracts=contracts)
    return render_template("create_bill.html",contracts=contracts)


@app.route("/generate_ifs_bill",methods=["POST"])
def generate_ifs_bill():
    if 'user_id' in session or "eic_user_id" not in session :
        return redirect(url_for('login'))
    
    ge_date = date.today().strftime("%d-%m-%Y")
    ifs_bill_data = {"ge_no":12345,
                     "rr_no":"23RAR-12345",
                     "ge_date": ge_date} 
    
    user_bill_data = session["bill_data"]
    user_bill_data.update(ifs_bill_data)

    return jsonify(user_bill_data)  



# Contract routes
@app.route('/wages')
def view_wages():
    if session['user_id'] != 'admin':
        flash("You are not authorized to access this page.", "error")
        return redirect(url_for('login'))
    wages = db_session.query(ManpowerWage).all()
    return render_template('view_wages.html', wages=wages)


# Contract form route
@app.route('/add_wage', methods=['POST'])
def add_wage():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        emp_category = request.form['emp_category']
        amount = int(request.form['amount'])
        
        
        new_wage = ManpowerWage(emp_category=emp_category,wage=amount)
        try:
            db_session.add(new_wage)
            db_session.commit()
        except SQLAlchemyError as e:
            db_session.rollback()
            error_message = str(e.orig)
            if 'UNIQUE constraint failed' in error_message:
                flash('Category already exists.', 'error')
            else:
                flash('Error occurred while adding user: {}'.format(error_message), 'error')
        return redirect(url_for('view_wages'))
    return redirect(url_for('view_wages'))


@app.route('/update_wage/<category>', methods=['POST'])
def update_wage(category):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    amount_update = int(request.form['amount_update'])
    wage = db_session.query(ManpowerWage).filter_by(emp_category=category).first()

    if wage:
        try:
            wage.wage = amount_update
            db_session.commit()
        except SQLAlchemyError as e:
            db_session.rollback()
            error_message = str(e.orig)
            flash('Error occurred while adding user: {}'.format(error_message), 'error')
    return redirect(url_for('view_wages'))

if __name__ == '__main__':
    app.run(debug=True)