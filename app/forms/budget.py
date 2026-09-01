"""
EventSphere - Budget Forms
"""

from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Email, Optional, Length
from app.models.budget import ExpenseCategory

class BudgetForm(FlaskForm):
    """Form to create or update an event budget."""
    total_amount = FloatField('Total Budget Amount (₹)', validators=[
        DataRequired(),
        NumberRange(min=0.0, message="Budget cannot be negative")
    ])
    submit = SubmitField('Save Budget')


class ExpenseForm(FlaskForm):
    """Form to request a new expense."""
    category = SelectField('Category', choices=ExpenseCategory.get_choices(), validators=[DataRequired()])
    amount = FloatField('Amount (₹)', validators=[
        DataRequired(),
        NumberRange(min=0.01, message="Expense must be greater than zero")
    ])
    description = StringField('Description', validators=[
        DataRequired(),
        Length(max=255)
    ])
    submit = SubmitField('Submit Expense')


class SponsorshipForm(FlaskForm):
    """Form to add a sponsorship."""
    sponsor_name = StringField('Sponsor Name', validators=[
        DataRequired(),
        Length(max=200)
    ])
    amount = FloatField('Sponsorship Amount (₹)', validators=[
        DataRequired(),
        NumberRange(min=0.01, message="Amount must be greater than zero")
    ])
    contact_email = StringField('Contact Email', validators=[
        Optional(),
        Email(message="Invalid email address")
    ])
    submit = SubmitField('Add Sponsorship')


class ApprovalActionForm(FlaskForm):
    """Form to approve or reject an expense."""
    action = SelectField('Action', choices=[('approve', 'Approve'), ('reject', 'Reject')], validators=[DataRequired()])
    notes = TextAreaField('Notes (Optional)')
    submit = SubmitField('Process')
