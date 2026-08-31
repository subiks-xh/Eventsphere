"""
EventSphere - Authentication Forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models.user import User, UserRole


class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Username', validators=[
        DataRequired(message="Username is required")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required")
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(min=4, max=80, message="Username must be between 4 and 80 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address"),
        Length(max=120, message="Email must be less than 120 characters")
    ])
    first_name = StringField('First Name', validators=[
        DataRequired(message="First name is required"),
        Length(max=100, message="First name must be less than 100 characters")
    ])
    last_name = StringField('Last Name', validators=[
        Length(max=100, message="Last name must be less than 100 characters")
    ])
    phone = StringField('Phone', validators=[
        Length(max=20, message="Phone must be less than 20 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=6, message="Password must be at least 6 characters")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password"),
        EqualTo('password', message="Passwords must match")
    ])
    role = SelectField('Role', choices=UserRole.get_choices(), default=UserRole.ATTENDEE)
    submit = SubmitField('Register')

    def validate_username(self, field):
        """Check if username already exists."""
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, field):
        """Check if email already exists."""
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('Email already exists. Please use a different email.')
