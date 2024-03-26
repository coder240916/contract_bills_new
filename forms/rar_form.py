from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, DateField, SubmitField, SelectField,FloatField
from wtforms.validators import InputRequired, NumberRange
# from sqlalchemy import distinct
# from data_model_flask_alchemy import db,BillOfQuantities

# Create a WTForms form class for fixed fields
class FixedForm(FlaskForm):
    contract_no = SelectField('Contract Number', validators=[InputRequired()],coerce=str)
    invoice_number = StringField('Invoice Number', validators=[InputRequired()])
    invoice_date = DateField('Invoice Date', validators=[InputRequired()], format='%Y-%m-%d')
    rar_no = SelectField('RAR Number', validators=[InputRequired()])
    month_select = SelectField('Select Month', validators=[InputRequired()])
    submit = SubmitField('Submit', validators=[])

    def __init__(self, *args, contracts=None,month_dict=None,session_attendance_data=None,**kwargs):
        super(FixedForm, self).__init__(*args, **kwargs)
        # Populate contract numbers in the dropdown
        if contracts:
            self.contract_no.choices = [(contract.contract_no, contract.contract_no) for contract in contracts]

        # selected_month = session_attendance_data["selected_month"]
        # if selected_month in month_dict.values():
        self.month_select.choices = [(month_year, month) for month, month_year in month_dict.items()]
        # self.month_select.default = selected_month

            
        self.rar_no.choices = [(i,i) for i in range(1,25)]

# Dynamically add fields to the form based on unique descriptions in the database
def create_dynamic_form(unique_descriptions):
    class DynamicForm(FlaskForm):
        pass   
    
    #unique_descriptions = db.session.query(distinct(BillOfQuantities.description)).all()
    for sl_no,description in unique_descriptions:
        field_name = f"field_{sl_no}"  # Dynamic field name based on sl_no       
        setattr(DynamicForm, field_name, FloatField(label=f"SL No: {sl_no} - {description}"))

    DynamicForm.unique_descriptions = unique_descriptions

    return DynamicForm

