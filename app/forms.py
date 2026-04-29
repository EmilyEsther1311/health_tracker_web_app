from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField,DateTimeLocalField, RadioField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import IntegerField, FloatField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Email, EqualTo
from flask_wtf.file import FileField, FileAllowed

from app.models import User
from app import db
import sqlalchemy as sa


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ExerciseTypeForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    duration = IntegerField('Duration (to nearest min)', validators=[DataRequired(), NumberRange(min=0)])
    intensity = RadioField('Intensity', choices=[(1,"1 = Very easy"),(2,"2 = Easy"), (3,"3 = Moderate"), (4,"4 = Hard"),(5,"5 = Very hard")], validators=[DataRequired()])
    attachment = FileField("Upload supporting file (optional)",validators=[FileAllowed(['jpg', 'png', 'pdf'], 'Images and PDFs only')])
    submit = SubmitField('Add exercise type')

class ActivityForm(FlaskForm):
    start_time = DateTimeLocalField('Start time', validators=[DataRequired()])
    end_time = DateTimeLocalField('End time', validators=[DataRequired()])
    notes = StringField('Notes')
    exercise_type_id = SelectField("Exercise type", coerce=int)
    submit = SubmitField('Record activity')

    def validate_end_time(self, field):
        if self.start_time.data and field.data:
            if field.data < self.start_time.data:
                raise ValidationError("End time cannot be before start time.")

class BodyMeasurementForm(FlaskForm):
    weight = FloatField('Weight (kg)', validators=[DataRequired(), NumberRange(min=0)])
    pulse = IntegerField('Pulse (bpm)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Record body measurement')

class CalendarForm(FlaskForm):
    start_date = DateField('Start date', validators=[DataRequired()])
    end_date = DateField('End date', validators=[DataRequired()])
    submit = SubmitField('Generate report')

    def validate_end_date(self, field):
        if self.start_date.data and field.data:
            if field.data < self.start_date.data:
                raise ValidationError("End date cannot be before start date.")

class SupportGroupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add support group')