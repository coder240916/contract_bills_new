from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, DateField, SubmitField, SelectField,FloatField
from wtforms.validators import InputRequired, NumberRange


class BillDocsForm(FlaskForm):
    contract_no = SelectField('Contract Number', validators=[InputRequired()],coerce=str)
    ge_number = IntegerField('Gate Entry Number', validators=[InputRequired()])
    ge_date = DateField('Gate Entry Date', validators=[InputRequired()], format='%Y-%m-%d')
    rr_no = StringField('RR Number', validators=[InputRequired()])
    rar_no = SelectField('RAR Number', validators=[InputRequired()])
    month_select = SelectField('Select Month', validators=[InputRequired()])
    submit = SubmitField('Submit', validators=[])

    def __init__(self, *args, contracts=None,month_dict=None,default_month=None,**kwargs):
        super(BillDocsForm, self).__init__(*args, **kwargs)
        # Populate contract numbers in the dropdown
        if contracts:
            self.contract_no.choices = [(contract.contract_no, contract.contract_no) for contract in contracts]

        # selected_month = session_attendance_data["selected_month"]
        # if selected_month in month_dict.values():
        self.month_select.default = default_month
        self.month_select.choices = [(month_year, month) for month, month_year in month_dict.items()]
        # self.month_select.default = selected_month

            
        self.rar_no.choices = [(i,i) for i in range(1,25)]

