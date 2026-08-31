"""
EventSphere - Feedback Forms
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional


class FeedbackForm(FlaskForm):
    """Form for submitting feedback."""
    rating = IntegerField('Rating (1-5)', validators=[
        DataRequired(message="Rating is required"),
        NumberRange(min=1, max=5, message="Rating must be between 1 and 5")
    ])
    comments = TextAreaField('Comments', validators=[
        Length(max=1000, message="Comments must be less than 1000 characters")
    ])
    suggestions = TextAreaField('Suggestions', validators=[
        Length(max=1000, message="Suggestions must be less than 1000 characters")
    ])
    submit = SubmitField('Submit Feedback')
