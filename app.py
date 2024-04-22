import os

import calendar
import pandas as pd
from datetime import datetime,date

from sqlalchemy import and_,distinct
from utils.app_db_operations import insert_or_update_bills_boq_lines, insert_or_update_contract_bill, check_values_exists_in_bills_table,check_invoice_in_bills_tables
from utils.punch_processing import process_punch_df, get_saved_punch_data
from utils.attendance_form import read_punching_data

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from sqlalchemy.exc import SQLAlchemyError
from data_model_flask_alchemy import Contract, User, ContractEmployee, ManpowerWage, BillOfQuantities, ContractBills, db
from werkzeug.security import generate_password_hash, check_password_hash
from utils.utils import generate_data,generate_abstract,BILLS_FOLDER_PATH,get_prev_months,generate_attendance_data
from utils.utils import generate_attendance_data_df,split_list,attendance_to_csv,get_month_name
from utils.attendance_form import attendance_processing,generate_attendance_excel
from utils.pf_esi_format import pf_esi_preprocessing,generate_pf_esi_sheet,create_pf_esi_sheet
from utils.wage_calc import wage_calc_preprocessing,generate_wage_calc_sheet,create_wage_calc_sheet
from utils.rar_abstract import get_rar_quantities
from utils.bill_docs import get_latest_excel_file, get_from_and_to_dates, get_checklist_form_data, get_undertaking_form_data, generate_checklist_sheet
from flask_bcrypt import Bcrypt
from forms.rar_form import FixedForm,create_dynamic_form
from forms.bill_docs_form import BillDocsForm

from utils.admin_contract_docs import get_contract_docs_data, generate_download_links,generate_sample_df

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key
app.static_folder = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contract_bills.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bcrypt = Bcrypt(app)

db.init_app(app)


with app.app_context():
    db.create_all()

    # Admin credentials
    # Add admin user if not exists
    admin_user = User.query.filter_by(username='admin').first()
    print(admin_user)

    if not admin_user:
        admin_password_hash = bcrypt.generate_password_hash('admin')
        admin_user = User(username='admin', password_hash=admin_password_hash)
        db.session.add(admin_user)
        db.session.commit()

    # Login route
    @app.route('/', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            # Check if the user is admin
            if username == 'admin':
                user = User.query.filter_by(username=username).first()
                if user and bcrypt.check_password_hash(user.password_hash, password):
                    session['user_id'] = user.username
                    return redirect(url_for('view_contracts'))
                else:
                    flash("Invalid username or password.", "error")
                    return render_template('login_test.html')
            
            # For non-admin users, check both users and contracts table
            else:
                # Check if the user exists in the users table
                user = User.query.filter_by(username=username).first()
                if user and bcrypt.check_password_hash(user.password_hash, password):
                    # Check if the user exists in the contracts table with either eic_pbno or oic_pbno
                    contract = Contract.query.filter(
                        (Contract.eic_pbno == username) | (Contract.oic_pbno == username)
                    ).first()

                    if contract and contract.eic_pbno == username:
                        session['eic_user_id'] = user.username
                        return redirect(url_for('eic_dashboard'))
                    elif contract and contract.oic_pbno == username:
                        session['oic_user_id'] = user.username
                        return redirect(url_for('oic_dashboard'))
                    else:
                        flash("You are not authorized to access the system.", "error")
                        return render_template('login.html')
                else:
                    flash("Invalid username or password.", "error")
                    return render_template('login.html')
        return render_template('login_test.html')

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
        
        contracts = Contract.query.filter(Contract.eic_pbno == session['eic_user_id']).all()
        return render_template('eic_dashboard.html', no_of_contracts=len(contracts))

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
        
        contracts = Contract.query.all()
        print(contracts)
        return render_template('view_contracts.html', contracts=contracts)

    # User routes
    @app.route('/users')
    def view_users():
        if session['user_id'] != 'admin':
            flash("You are not authorized to access this page.", "error")
            return redirect(url_for('login'))
        users = User.query.all()
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
            eic_dept_no = request.form["eic_dept_no"]
            work_order_no = request.form["work_order_no"]
            gem_contract_no = request.form["gem_order_no"]
            
            new_contract = Contract(contract_no=contract_no, eic_pbno=eic_pbno, oic_pbno=oic_pbno, contract_type=contract_type, 
                                    start_date=start_date,duration_months = duration_months,bill_frequency = bill_frequency,contract_value=contract_value,
                                    contract_description = contract_description,vendor_id=vendor_id,vendor_name=vendor_name,
                                    vendor_address = vendor_address,vendor_gst=vendor_gst,eic_dept_no=eic_dept_no,work_order_no=work_order_no,gem_contract_no=gem_contract_no)
            with app.app_context():
                # Add the contract to the session and commit
                db.session.add(new_contract)
                db.session.commit()
            
            return redirect(url_for('view_contracts'))
        return redirect(url_for('view_contracts'))


    @app.route('/delete_contract/<contract_no>', methods=['POST'])
    def delete_contract(contract_no):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        contract = db.session.query(Contract).filter_by(contract_no=contract_no).first()
        if contract:
            db.session.delete(contract)
            db.session.commit()
        return redirect(url_for('view_contracts'))


    @app.route('/update_contract/<contract_no>', methods=['POST'])
    def update_contract(contract_no):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        eic_pbno_update = int(request.form['eic_pbno_update'])
        oic_pbno_update = int(request.form['oic_pbno_update'])

        contract = db.session.query(Contract).filter_by(contract_no=contract_no).first()
        if contract:
            contract.eic_pbno = eic_pbno_update
            contract.oic_pbno = oic_pbno_update
            db.session.commit()
        return redirect(url_for('view_contracts'))


    # Add User route
    @app.route('/add_user', methods=['POST'])
    def add_user():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists
        existing_user = db.session.query(User).filter_by(username=username).first()
        if existing_user:
            flash("User with this username already exists.", "error")
            return redirect(url_for('view_users'))

        # Hash the password
        password_hash = bcrypt.generate_password_hash(password)
        
        # Create a new user
        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('view_users'))

    # Delete User route
    @app.route('/delete_user/<int:user_id>', methods=['POST'])
    def delete_user(user_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        # Query the user by user_id
        user_to_delete = db.session.query(User).filter_by(user_id=user_id).first()
        
        # Check if the user exists
        if not user_to_delete:
            flash("User Not found", "error")
            return redirect(url_for('view_users'))
        
        # Delete the user
        db.session.delete(user_to_delete)
        db.session.commit()
        
        return redirect(url_for('view_users'))


    @app.route('/manpower')
    def manpower():
        if 'user_id' in session or "eic_user_id" not in session :
            return redirect(url_for('login'))
        contracts = db.session.query(Contract).filter_by(eic_pbno=session["eic_user_id"]).all()
        contract_nos = [contract.contract_no for contract in contracts]
        employees = db.session.query(ContractEmployee).filter(ContractEmployee.contract_no.in_(contract_nos)).all()
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
                db.session.add(new_employee)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
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
        
        employee = db.session.query(ContractEmployee).filter_by(emp_punch_id=emp_punch_id).first()
        if employee:
            db.session.delete(employee)
            db.session.commit()
        return redirect(url_for('manpower'))


    @app.route('/update_manpower/<emp_punch_id>', methods=['POST'])
    def update_manpower(emp_punch_id):
        if 'user_id' in session or "eic_user_id" not in session :
            return redirect(url_for('login'))

        emp_name_update = request.form['emp_name']
        contract_no_update = request.form['contract_no']

        employee = db.session.query(ContractEmployee).filter_by(emp_punch_id=emp_punch_id).first()
        contracts = db.session.query(Contract).filter_by( eic_pbno=session["eic_user_id"]).all()
        contract_nos = [contract.contract_no for contract in contracts]

        if contract_no_update not in contract_nos:
            flash("Invalid Contract No.Please enter valid contract no or contact admin", "error")
            return redirect(url_for('manpower'))


        if employee:
            employee.emp_name = emp_name_update
            employee.contract_no = contract_no_update
            db.session.commit()
        return redirect(url_for('manpower'))


    # attendance endpoint
    @app.route("/punching_data",methods=["GET","POST"])
    def punching_data():
        if 'user_id' in session or "eic_user_id" not in session :
            return redirect(url_for('login'))
        
        
        punch_df,hover_df = process_punch_df("utils/punch_data.xlsx",3,2024)
        punch_df.reset_index(inplace=True)
        
        saved_punch_data = get_saved_punch_data("utils/updated_punch_data.csv")
        

        if saved_punch_data is not None:
            punch_df = saved_punch_data
            print(str(punch_df))

        
        # print(str(punch_df))
        
        if request.method == 'POST':
        # Update DataFrame with edited values
            # print(request.form)
            for key in request.form:
                # print(key)
                if 'cell' in key:
                    row,col = key.split('_')[1:]
                    punch_df.iloc[int(row), int(col)] = request.form[key]
            # Save or process the updated DataFrame here
        hover_data = [[[str(x) for x in dt] if dt != "No Punch" else "No Punch" for dt in sublist ] for sublist in hover_df.values.tolist() ]

        if 'final_submission' in request.form:
            # print(request.form)
            # Save the updated DataFrame to a CSV file
            #punch_df.to_csv('updated_punch_data.csv', index=False)  # Change the file pa
            punch_df.to_csv('utils/updated_punch_data.csv', index=False) 
        # Convert DataFrame to HTML table with editable cells
        # html_table = attendance_df.to_html(classes='table table-bordered table-hover', index=True, escape=False,
        #                         header="true", table_id="editable")
        return render_template('punching.html', punch_df=punch_df, hover_data=hover_data)

    # attendance endpoint
    @app.route("/attendance1",methods=["GET","POST"])
    def attendance1():
        if 'user_id' in session or "eic_user_id" not in session :
            return redirect(url_for('login'))
        
        month_dict = get_prev_months()
        
        present_month = date.today().month
        month_dict.pop(get_month_name(present_month))   

        contracts = db.session.query(Contract).filter(Contract.eic_pbno == session["eic_user_id"])

        if request.method == "POST":
            month,year = request.form["month_select"].split("-")
            selected_month = request.form["month_select"]
        
            contract_no = request.form["contract_select"]
            nh_days = int(request.form["nh_days"])

            month_name = get_month_name(int(month))

            selected_values = {"selected_month":selected_month,"selected_contract_no":contract_no,"selected_nh_days":nh_days,"month_name":month_name,"year":year}

            attendance_df,sunday_columns = read_punching_data(nh_days)
            
            
            return render_template("attendance_form_1.html",month_dict=month_dict,contracts=contracts,selected_values=selected_values,
                                   attendance_df=attendance_df,sunday_columns=sunday_columns)


        return render_template("attendance_form_1.html",month_dict=month_dict,contracts=contracts)
            

    # download attendance form
    @app.route("/download_attendance1",methods=["POST"])
    def download_attendance1():

        wages_data = ManpowerWage.query.all()
        wages_list = [[wage.emp_category.upper(),float(wage.wage)] for wage in wages_data]
        wages = pd.DataFrame(wages_list,columns=["CATEGORY","Wage per day"])

        
        #wages = pd.DataFrame({"CATEGORY":['SKILLED',"SEMI-SKILLED","UNSKILLED"],"Wage per day":[709,589,504]})

        if request.method == "POST":
            prof_tax = float(request.form["prof_tax"])
            ld = float(request.form["ld"])
            penalty = float(request.form["penalty"])
            taxes = float(request.form["taxes"])
            other_recovery = float(request.form["other_recovery"])

            month, year = session["attendance_data"].get("month"), session["attendance_data"].get("year")
            contract_no = session["attendance_data"].get("contract_no")
            emp_categories = session["attendance_data"].get("skill_categories")

            result_df, sunday_list = attendance_processing(month,year,contract_no, emp_categories)

        return "downloaded"

    # attendance endpoint
    @app.route("/attendance",methods=["GET","POST"])
    def attendance():
        if 'user_id' in session or "eic_user_id" not in session :
            return redirect(url_for('login'))
        
        month_dict = get_prev_months()

        contracts = db.session.query(Contract).filter(Contract.eic_pbno == session["eic_user_id"])

        if request.args.get("auto_submit"):
            flash("Attendance Saved successfully!", "success")
            return render_template("attendance_form.html",
                                   contracts=contracts,
                                   month_dict=month_dict,
                                   attendance_data=None,
                                   session_attendance_data=session["attendance_data"],
                                   auto_submit=True)

        if request.args.get("download"):
            flash("Attendance Form Downloaded successfully!", "success")
            return render_template("attendance_form.html",
                                   contracts=contracts,
                                   month_dict=month_dict,
                                   attendance_data=None,
                                   session_attendance_data=session["attendance_data"],
                                   auto_submit=True)

        if request.method == "POST":
            month,year = request.form["month_select"].split("-")
            selected_month = request.form["month_select"]
        
            contract_no = request.form["contract_select"]
            
            employees = db.session.query(ContractEmployee).filter_by(contract_no=contract_no).all()
            employee_names = [employee.emp_name for employee in employees]
            skill_categories = [employee.emp_category.upper() for employee in employees]


            month_name = get_month_name(int(month))
            session["attendance_data"] = {"month": int(month),"month_name":month_name,"year": int(year),
                                          "contract_no": contract_no,"employees": employee_names,
                                          "skill_categories": skill_categories,"selected_month":selected_month}


            attendance_data = generate_attendance_data_df(employee_names,int(month),int(year),contract_no)
            print(attendance_data)

            return render_template("attendance_form.html",
                                   attendance_data=attendance_data,
                                   contracts=contracts,
                                   month_dict=month_dict,
                                   session_attendance_data = session["attendance_data"]

                                   )

        return render_template("attendance_form.html",contracts=contracts,month_dict=month_dict,attendance_data=None)


    @app.route("/save_attendance",methods=["POST"])
    def save_attendance():
        updated_attendance = [float(val) for val in request.form['attendance_data'][1:-1].split(",")]
        month,year = session["attendance_data"].get("month"),session["attendance_data"].get("year")
        employees = session["attendance_data"].get("employees")
        contract_no = session["attendance_data"].get("contract_no")

        # print(employees)
        # print(session["attendance_data"])
        # print(updated_attendance)

        values = split_list(updated_attendance,len(employees))
        # print(values)
        target_data = generate_attendance_data_df(employees,month,year,contract_no,values)
       
        data = pd.DataFrame(target_data).iloc[:-1,:]
        
        status_msg = attendance_to_csv(month,year,contract_no,data)


        return redirect(url_for('attendance',auto_submit=True))

    # download attendance form
    @app.route("/download_attendance",methods=["POST"])
    def download_attendance():

        wages_data = ManpowerWage.query.all()
        wages_list = [[wage.emp_category.upper(),float(wage.wage)] for wage in wages_data]
        wages = pd.DataFrame(wages_list,columns=["CATEGORY","Wage per day"])

        
        #wages = pd.DataFrame({"CATEGORY":['SKILLED',"SEMI-SKILLED","UNSKILLED"],"Wage per day":[709,589,504]})

        if request.method == "POST":
            prof_tax = float(request.form["prof_tax"])
            ld = float(request.form["ld"])
            penalty = float(request.form["penalty"])
            taxes = float(request.form["taxes"])
            other_recovery = float(request.form["other_recovery"])
            
            month, year = session["attendance_data"].get("month"), session["attendance_data"].get("year")
            contract_no = session["attendance_data"].get("contract_no")
            emp_categories = session["attendance_data"].get("skill_categories")

            result_df, sunday_list = attendance_processing(month,year,contract_no, emp_categories)
            print(str(result_df))
            print(sunday_list)

            total_pay_days = result_df["TOTAL PAY DAYS"].sum()

            contract = db.session.query(Contract).filter(Contract.contract_no == contract_no).first()
            work_description,vendor_name = contract.contract_description,contract.vendor_name
            contract_st_dt = contract.start_date
            dept_name,dept_intercom = contract.department.dept_name,contract.department.dept_phone_no
            work_order_no,gem_contract_no = contract.work_order_no,contract.gem_contract_no


            file_path = generate_attendance_excel(result_df, month, year, work_description,contract_no,
                                dept_name, dept_intercom, vendor_name,
                                work_order_no, gem_contract_no, contract_st_dt,
                                sunday_list,total_pay_days)
            
            pf_esi_processed_df,bill_pay_days,rows_yellow_fill = pf_esi_preprocessing(file_path,wages,prof_tax)
            pf_epf_sheet = generate_pf_esi_sheet(pf_esi_processed_df,rows_yellow_fill,month,year,vendor_name)
            target_path = create_pf_esi_sheet(month,year,contract_no,pf_epf_sheet)
            print(bill_pay_days)

            #session["rar_abstract_data"] = bill_pay_days

            result = BillOfQuantities.query.filter( and_( 
                                                      BillOfQuantities.description.ilike('%service charges%'), 
                                                      BillOfQuantities.contract_no == contract_no)
                                                      ).order_by(BillOfQuantities.sl_no).all()
            
            service_charges = []
            for item in result:
                service_charges.append(float(item.rate))
            service_charges = sorted(service_charges,reverse=True)
            
            wage_calc_df = wage_calc_preprocessing(bill_pay_days,wages)
            wage_calc_sheet = generate_wage_calc_sheet(month,year,wage_calc_df,bill_pay_days,service_charges,ld,penalty,taxes,other_recovery,contract_no,vendor_name)
            target_path = create_wage_calc_sheet(month,year,contract_no,wage_calc_sheet)
            print(target_path)

            # return redirect(url_for('attendance',download=True))
            return send_file(target_path,as_attachment=True)


    # create bill for EIC users
    @app.route("/create_abstract",methods=["GET","POST"])
    def create_abstract():
        if 'user_id' in session or "eic_user_id" not in session :
            return redirect(url_for('login'))
        
        contracts = db.session.query(Contract).filter(Contract.eic_pbno == session["eic_user_id"])
        
        month_dict = get_prev_months()
        fixed_form = FixedForm(contracts=contracts,month_dict=month_dict,session_attendance_data=None)
        # fixed_form.month_select.default = session["attendance_data"].get("selected_month")
        dynamic_form = None
        present_rar_qty = None

        if request.method == "POST" and fixed_form.validate(): 


            session["rar_abstract_data"] = {"contract_no":fixed_form.contract_no.data,
                                            "rar_no":fixed_form.rar_no.data,
                                            "invoice_no":fixed_form.invoice_number.data,
                                            "invoice_date":fixed_form.invoice_date.data,
                                            "selected_month":request.form["month_select"]}
            
            check_invoice_exists = check_invoice_in_bills_tables(session)
            if check_invoice_exists:
                flash(check_invoice_exists,"error")
                return render_template('rar_page.html', fixed_form=fixed_form, dynamic_form=dynamic_form,present_rar_qty=present_rar_qty)

            boq_lines = db.session.query(BillOfQuantities).filter(BillOfQuantities.contract_no == "22SNCJO-373").all()
            unique_descriptions = [[boq_line.sl_no,boq_line.description] for boq_line in boq_lines]
            dynamic_form = create_dynamic_form(unique_descriptions)
            form = dynamic_form(request.form)

            present_rar_qty = get_rar_quantities(session_rar_abstract_data= session["rar_abstract_data"], descriptions=unique_descriptions)

            # print(request.form)
            # print(form.errors)
            # print(form.validate())

            if "field_1" in request.form and form.validate():
                
                present_rar_qty = [request.form.get(f"field_{i}") for i in range(1,len(unique_descriptions)+1)]
                session["rar_abstract_data"]["ppiresent_rar_qty"] = present_rar_qty
                flash(str(session["rar_abstract_data"]),"session")

                contract_no = session["rar_abstract_data"].get("contract_no")
                rar_no = session["rar_abstract_data"].get("rar_no")

                for boq_line_no,value in enumerate(present_rar_qty,start=1):
                    row = (contract_no,boq_line_no,rar_no,value)
                    status_msg = insert_or_update_bills_boq_lines(*row)
                    if "Error" in status_msg:
                        flash(status_msg,"error")
                    else:
                        flash(status_msg,"success")

                            
                return render_template('rar_page.html', fixed_form=fixed_form, dynamic_form=dynamic_form,present_rar_qty=present_rar_qty)
            
        return render_template('rar_page.html', fixed_form=fixed_form, dynamic_form=dynamic_form,present_rar_qty=present_rar_qty)


    @app.route("/bill_docs",methods=["GET","POST"])
    def bill_docs():
        if 'user_id' in session or "eic_user_id" not in session :
            return redirect(url_for('login'))
        
        contracts = db.session.query(Contract).filter(Contract.eic_pbno == session["eic_user_id"])

        contract_no = [contract.contract_no for contract in contracts][0]
        
        month_dict = get_prev_months()

        latest_excel_file = get_latest_excel_file(contract_no).split("_")

        month_year = "-".join(latest_excel_file[-2:]).split(".")[0]

        fixed_form = BillDocsForm(contracts=contracts,month_dict=month_dict,default_month=month_year)

        checklist_form_data = None

        undertaking_form_data = None

        if request.method == "POST" and fixed_form.validate(): 

            contract_no = request.form["contract_no"] 

            contract = db.session.query(Contract).filter(Contract.contract_no == contract_no).first()
            
            selected_month = request.form["month_select"]
            bill_from_date,bill_to_date = get_from_and_to_dates(contract_no,selected_month)

            checklist_form_data = get_checklist_form_data(contract)

            session["checklist_data"] = {"contract_no":fixed_form.contract_no.data,
                                            "ge_number":fixed_form.ge_number.data,
                                            "ge_date":fixed_form.ge_date.data.strftime("%d-%m-%Y"),
                                            "rr_no":fixed_form.rr_no.data,
                                            "rar_no":fixed_form.rar_no.data,
                                            "selected_month":request.form["month_select"]}

            check_status = check_values_exists_in_bills_table(session)
            if check_status:
                flash(check_status,"error")
                return render_template('bill_docs_form.html', fixed_form=fixed_form, checklist_form_data=None,undertaking_form_data=None)

            if "checklist_field_1" in request.form and fixed_form.validate():

                user_entered_values = [request.form[f"checklist_field_{i}"].replace(r"\s+"," ") for i in range(1,39)]

                generate_checklist_sheet(checklist_data = session["checklist_data"],contract=contract,values=user_entered_values)

                flash("Checklist generated successfully","success")

                undertaking_form_data = get_undertaking_form_data()
                checklist_form_data = None

            if "undertaking_field_1" in request.form and fixed_form.validate():
                
                flash("Undertaking sheet generated successfully","success")
                flash("Please wait,the files are being downloaded..","success")
                checklist_form_data = None
                undertaking_form_data = None

                ge_no = session["checklist_data"].get("ge_number")
                rar_no = session["checklist_data"].get("rar_no")
                ge_date = datetime.strptime(session["checklist_data"].get("ge_date"), '%d-%m-%Y').date()
                rr_no = session["checklist_data"].get("rr_no")
                invoice_amount = float(request.form["undertaking_field_1"])
                invoice_date = datetime.strptime("2024-04-06",'%Y-%m-%d').date()
                penalty = 15000.00

                row = ge_no, contract_no, rar_no, "UE/B/2022/43",invoice_date, invoice_amount, ge_date, rr_no, penalty, invoice_date, invoice_date, None

                status_msg = insert_or_update_contract_bill(*row)

                if "Error" in status_msg:
                    flash(status_msg,"error")
                else:
                    flash(status_msg,"success")


                return render_template('bill_docs_form.html', fixed_form=fixed_form,checklist_form_data=None,undertaking_form_data=None)

        return render_template('bill_docs_form.html', fixed_form=fixed_form, checklist_form_data=checklist_form_data,undertaking_form_data=undertaking_form_data)



    @app.route("/contract_docs",methods=["GET","POST"])
    def contract_docs():
        if 'user_id' in session or "eic_user_id" not in session :
            return redirect(url_for('login'))
        
        contracts = db.session.query(Contract).filter(Contract.eic_pbno == session["eic_user_id"])
        print(request.args)

        if request.args.get("bills") :
            message = session["contract_docs"].get("status_message")
            print(message)

            if "Error" in message:
                flash(message, "error")
            else:
                flash(message, "success")

            contract_no = session["contract_docs"].get("contract_no")
            
            contract_bills = db.session.query(ContractBills).filter_by(contract_no=contract_no).all()
            return render_template("bills.html",contracts=contracts,contract_bills=contract_bills)

        if request.method == "POST":
            contract_no = request.form["contract_select"]
            contract_bills = db.session.query(ContractBills).filter_by(contract_no=contract_no).all()

            return render_template("bills.html",contracts=contracts,contract_bills=contract_bills)
        
        return render_template("bills.html",contracts=contracts)


    @app.route("/contract_docs/<string:contract_no>/<int:rar_no>",methods=["POST"])
    def update_payment_date(contract_no,rar_no):
        if 'user_id' in session or "eic_user_id" not in session :
            return redirect(url_for('login'))
        
        if request.method == "POST":
            # contract_no = request.form["contract_no"]
            # rar_no = request.form["rar_no"]
            # session["contract_docs"] = {"contract_no":contract_no}
            bill_payment_date = datetime.strptime(request.form["new_bill_payment_date"],"%Y-%m-%d").date()

            bill = db.session.query(ContractBills).filter_by(contract_no=contract_no,rar_no=rar_no).first()

            try:
                bill.bill_payment_date = bill_payment_date
                db.session.commit()
                
                message = "Payment date updated successfully"
                
            except SQLAlchemyError as e:
                db.session.rollback()
                message = f"Error updating payment date,{str(e)}"

            session["contract_docs"] = {"status_message":message,"contract_no":contract_no}
        return redirect(url_for("contract_docs",bills=True))


    # Contract routes
    @app.route('/wages')
    def view_wages():
        if session['user_id'] != 'admin':
            flash("You are not authorized to access this page.", "error")
            return redirect(url_for('login'))
        wages = db.session.query(ManpowerWage).all()
        return render_template('view_wages.html', wages=wages)


    # Contract form route
    @app.route('/add_wage', methods=['POST'])
    def add_wage():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            emp_category = request.form['emp_category']
            amount = float(request.form['amount'])
            
            
            new_wage = ManpowerWage(emp_category=emp_category,wage=amount)
            try:
                db.session.add(new_wage)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
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

        amount_update = float(request.form['amount_update'])
        wage = db.session.query(ManpowerWage).filter_by(emp_category=category).first()

        if wage:
            try:
                wage.wage = amount_update
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                error_message = str(e.orig)
                flash('Error occurred while adding user: {}'.format(error_message), 'error')
        return redirect(url_for('view_wages'))


    @app.route("/admin_contract_docs",methods=["GET","POST"])
    def admin_contract_docs():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        #contract_files = get_contract_docs_data()
        contracts = db.session.query(Contract).all()

        for contract in contracts:
            contract.contract_description = contract.contract_description.title()

        contract_files = {contract.contract_no: generate_download_links(contract.contract_no) for contract in contracts}
        
        payment_df = generate_sample_df()
        
        status_map = {'Green': '<div class="status-circle green"></div>',
              'Yellow': '<div class="status-circle yellow"></div>',
              'Red': '<div class="status-circle red"></div>'}

        payment_df['Status'] = payment_df['Status'].map(status_map)
        payment_df = payment_df.set_index("Month").T

        print(contract_files)       
        #payment_table_html = payment_df.to_html(classes='payment-table', index=True, escape=False)
        payment_table_html=None

        return render_template('admin_contract_docs_1.html',contracts=contracts, contract_files=contract_files,payment_table_html=payment_table_html)
    

    @app.route('/download')
    def download():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        path = request.args.get('path')
        if path:
            return send_file(path, as_attachment=True)
        else:
            return "File not found", 404
if __name__ == "__main__":
    app.run(debug=False)

