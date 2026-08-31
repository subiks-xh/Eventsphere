"""
EventSphere - Registration Forms
"""

from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Length, Optional


class RegistrationForm(FlaskForm):
    """Form for event registration with special requirements."""
    special_requirements = TextAreaField('Special Requirements', validators=[
        Length(max=500, message="Special requirements must be less than 500 characters")
    ])
    submit = SubmitField('Register for Event')
