"""
EventSphere - Vendor Forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional, ValidationError
from app.models.vendor import Vendor, VendorService
from app.models.user import User


class VendorForm(FlaskForm):
    """Form for creating and editing vendors."""
    user_id = SelectField('User', coerce=int, validators=[
        DataRequired(message="User is required")
    ])
    business_name = StringField('Business Name', validators=[
        DataRequired(message="Business name is required"),
        Length(max=200, message="Business name must be less than 200 characters")
    ])
    contact_person = StringField('Contact Person', validators=[
        DataRequired(message="Contact person is required"),
        Length(max=200, message="Contact person must be less than 200 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address"),
        Length(max=120, message="Email must be less than 120 characters")
    ])
    phone = StringField('Phone', validators=[
        DataRequired(message="Phone is required"),
        Length(max=20, message="Phone must be less than 20 characters")
    ])
    service = SelectField('Service', choices=VendorService.get_choices(), default=VendorService.OTHER)
    description = TextAreaField('Description', validators=[
        Length(max=1000, message="Description must be less than 1000 characters")
    ])
    address = TextAreaField('Address', validators=[
        Length(max=500, message="Address must be less than 500 characters")
    ])
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending')
    ], default='active')
    submit = SubmitField('Save Vendor')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate user choices (only vendors or users who can be vendors)
        users = User.query.order_by(User.username).all()
        self.user_id.choices = [(u.id, f"{u.username} ({u.full_name})") for u in users]
        self.user_id.choices.insert(0, (0, '-- Select User --'))

    def validate_user_id(self, field):
        """Check if user exists."""
        if field.data and field.data > 0:
            user = User.query.get(field.data)
            if not user:
                raise ValidationError('Selected user does not exist.')

    def validate_business_name(self, field):
        """Check if business name already exists."""
        vendor = Vendor.query.filter(
            Vendor.business_name.ilike(field.data.strip()),
            Vendor.id != self.id
        ).first()
        if vendor:
            raise ValidationError('A vendor with this business name already exists.')
