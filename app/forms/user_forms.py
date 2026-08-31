"""
EventSphere - User Forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Optional, ValidationError
from app.models.user import User, UserRole, UserStatus


class UserForm(FlaskForm):
    """Form for creating and editing users (admin only)."""
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
        Length(max=100, message="First name must be less than 100 characters")
    ])
    last_name = StringField('Last Name', validators=[
        Length(max=100, message="Last name must be less than 100 characters")
    ])
    phone = StringField('Phone', validators=[
        Length(max=20, message="Phone must be less than 20 characters")
    ])
    password = PasswordField('Password', validators=[
        Length(min=6, message="Password must be at least 6 characters")
    ])
    role = SelectField('Role', choices=UserRole.get_choices(), default=UserRole.ATTENDEE)
    status = SelectField('Status', choices=[
        (UserStatus.ACTIVE, 'Active'),
        (UserStatus.DISABLED, 'Disabled')
    ], default=UserStatus.ACTIVE)
    submit = SubmitField('Save User')

    def validate_username(self, field):
        """Check if username already exists (excluding current user)."""
        user = User.query.filter(
            User.username == field.data,
            User.id != self.id
        ).first()
        if user:
            raise ValidationError('Username already exists.')

    def validate_email(self, field):
        """Check if email already exists (excluding current user)."""
        user = User.query.filter(
            User.email == field.data,
            User.id != self.id
        ).first()
        if user:
            raise ValidationError('Email already exists.')
