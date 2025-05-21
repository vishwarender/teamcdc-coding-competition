from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from models import Registration, School
import re

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SchoolForm(FlaskForm):
    name = StringField('School Name', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Add School')

    def validate_name(self, name):
        school = School.query.filter_by(name=name.data).first()
        if school:
            raise ValidationError('This school is already registered.')

class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    grade = SelectField('Grade', choices=[(6, 'Grade 6'), (7, 'Grade 7'), (8, 'Grade 8'), 
                                        (9, 'Grade 9'), (10, 'Grade 10')], 
                      validators=[DataRequired()], coerce=int)
    whatsapp_number = StringField('WhatsApp Number', validators=[DataRequired(), Length(min=10, max=15)])
    school_id = SelectField('School', validators=[DataRequired()], coerce=int)
    team_members_count = SelectField('Team Members Count', 
                                  choices=[(1, '1 (Solo)'), (2, '2'), (3, '3')], 
                                  validators=[DataRequired()], coerce=int)
    society_name = StringField('Society Name (Optional)', validators=[Length(max=100)])
    president_name = StringField('President Name (Optional)', validators=[Length(max=100)])
    president_number = StringField('President Number (Optional)', validators=[Length(max=20)])
    teacher_name = StringField('Teacher Name (Optional)', validators=[Length(max=100)])
    teacher_number = StringField('Teacher In-Charge Number (Optional)', validators=[Length(max=20)])
    submit = SubmitField('Register')

    def validate_whatsapp_number(self, whatsapp_number):
        if not re.match(r'^\+?\d{10,15}$', whatsapp_number.data):
            raise ValidationError('Please enter a valid WhatsApp number.')

class SubmissionForm(FlaskForm):
    participant = SelectField('Select Your Name & School', validators=[DataRequired()], coerce=int)
    description = TextAreaField('Explain Your Project', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Submit Project')
