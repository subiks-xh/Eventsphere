"""
EventSphere - Venue Forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email, ValidationError
from app.models.venue import Venue


class VenueForm(FlaskForm):
    """Form for creating and editing venues."""
    name = StringField('Venue Name', validators=[
        DataRequired(message="Venue name is required"),
        Length(max=200, message="Venue name must be less than 200 characters")
    ])
    address = StringField('Address', validators=[
        DataRequired(message="Address is required"),
        Length(max=500, message="Address must be less than 500 characters")
    ])
    city = StringField('City', validators=[
        DataRequired(message="City is required"),
        Length(max=100, message="City must be less than 100 characters")
    ])
    state = StringField('State/Province', validators=[
        Length(max=100, message="State must be less than 100 characters")
    ])
    postal_code = StringField('Postal Code', validators=[
        Length(max=20, message="Postal code must be less than 20 characters")
    ])
    country = StringField('Country', validators=[
        DataRequired(message="Country is required"),
        Length(max=100, message="Country must be less than 100 characters")
    ])
    capacity = IntegerField('Capacity', validators=[
        NumberRange(min=0, message="Capacity must be a positive number")
    ], default=0)
    description = TextAreaField('Description', validators=[
        Length(max=1000, message="Description must be less than 1000 characters")
    ])
    contact_phone = StringField('Contact Phone', validators=[
        Length(max=20, message="Phone must be less than 20 characters")
    ])
    contact_email = StringField('Contact Email', validators=[
        Length(max=120, message="Email must be less than 120 characters"),
        Email(message="Please enter a valid email address")
    ])
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance')
    ], default='active')
    submit = SubmitField('Save Venue')

    def validate_name(self, field):
        """Check if venue name already exists (case-insensitive)."""
        venue = Venue.query.filter(
            Venue.name.ilike(field.data.strip()),
            Venue.id != self.id
        ).first()
        if venue:
            raise ValidationError('A venue with this name already exists.')
