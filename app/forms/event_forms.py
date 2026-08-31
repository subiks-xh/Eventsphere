"""
EventSphere - Event Forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from datetime import datetime, time
from app.models.event import Event, EventCategory, EventStatus
from app.models.venue import Venue


class EventForm(FlaskForm):
    """Form for creating and editing events."""
    name = StringField('Event Name', validators=[
        DataRequired(message="Event name is required"),
        Length(max=200, message="Event name must be less than 200 characters")
    ])
    description = TextAreaField('Description', validators=[
        Length(max=2000, message="Description must be less than 2000 characters")
    ])
    category = SelectField('Category', choices=EventCategory.get_choices(), default=EventCategory.OTHER)
    date = DateField('Date', format='%Y-%m-%d', validators=[
        DataRequired(message="Date is required")
    ])
    start_time = TimeField('Start Time', format='%H:%M', validators=[
        DataRequired(message="Start time is required")
    ])
    end_time = TimeField('End Time', format='%H:%M', validators=[
        DataRequired(message="End time is required")
    ])
    venue_id = SelectField('Venue', coerce=int, validators=[
        DataRequired(message="Venue is required")
    ])
    capacity = IntegerField('Capacity', validators=[
        NumberRange(min=0, message="Capacity must be a positive number")
    ], default=0)
    registration_deadline = DateField('Registration Deadline', format='%Y-%m-%d')
    status = SelectField('Status', choices=EventStatus.get_choices(), default=EventStatus.DRAFT)
    image = StringField('Image URL', validators=[
        Length(max=256, message="Image URL must be less than 256 characters")
    ])
    submit = SubmitField('Save Event')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate venue choices
        venues = Venue.query.order_by(Venue.name).all()
        self.venue_id.choices = [(v.id, v.name) for v in venues]
        # Add empty choice at the beginning
        self.venue_id.choices.insert(0, (0, '-- Select Venue --'))

    def validate_end_time(self, field):
        """Check if end time is after start time."""
        if self.start_time.data and field.data:
            if field.data <= self.start_time.data:
                raise ValidationError('End time must be after start time.')

    def validate_venue_id(self, field):
        """Check if venue exists."""
        if field.data and field.data > 0:
            venue = Venue.query.get(field.data)
            if not venue:
                raise ValidationError('Selected venue does not exist.')

    def validate_registration_deadline(self, field):
        """Check if registration deadline is before event date."""
        if field.data and self.date.data:
            if field.data >= self.date.data:
                raise ValidationError('Registration deadline must be before event date.')
