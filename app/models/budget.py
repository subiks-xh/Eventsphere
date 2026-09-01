"""
EventSphere - Budget Models
"""

from datetime import datetime
from app import db


class ExpenseCategory:
    """Expense categories."""
    VENUE = 'venue'
    CATERING = 'catering'
    STAFFING = 'staffing'
    MARKETING = 'marketing'
    LOGISTICS = 'logistics'
    EQUIPMENT = 'equipment'
    OTHER = 'other'

    @classmethod
    def get_choices(cls):
        return [
            (cls.VENUE, 'Venue'),
            (cls.CATERING, 'Catering'),
            (cls.STAFFING, 'Staffing'),
            (cls.MARKETING, 'Marketing'),
            (cls.LOGISTICS, 'Logistics'),
            (cls.EQUIPMENT, 'Equipment'),
            (cls.OTHER, 'Other')
        ]


class ExpenseStatus:
    """Expense statuses."""
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'


class Budget(db.Model):
    """Budget model representing an event's budget."""
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, unique=True, index=True)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    expenses = db.relationship('Expense', backref='budget', foreign_keys='Expense.budget_id', lazy=True, cascade='all, delete-orphan')

    @property
    def approved_expenses_total(self):
        """Calculate total amount of approved expenses."""
        return sum(e.amount for e in self.expenses if e.status == ExpenseStatus.APPROVED)

    @property
    def remaining_budget(self):
        """Calculate remaining budget."""
        return self.total_amount - self.approved_expenses_total

    @property
    def utilization_percentage(self):
        """Calculate budget utilization percentage."""
        if self.total_amount <= 0:
            return 0.0
        return (self.approved_expenses_total / self.total_amount) * 100


class Expense(db.Model):
    """Expense model representing a single expense under a budget."""
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default=ExpenseCategory.OTHER)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default=ExpenseStatus.PENDING)
    
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    approval_request = db.relationship('ApprovalRequest', backref='expense', uselist=False, cascade='all, delete-orphan')
    requester = db.relationship('User', foreign_keys=[requested_by])
    approver = db.relationship('User', foreign_keys=[approved_by])
    
    def process_auto_approval(self, threshold=50000.0):
        """Auto-approve if amount is below threshold, otherwise create approval request."""
        from app.models.approval import ApprovalRequest
        if self.amount <= threshold:
            self.status = ExpenseStatus.APPROVED
            return True, None
        else:
            self.status = ExpenseStatus.PENDING
            # We defer creating the ApprovalRequest to the caller/service to easily commit it
            return False, ApprovalRequest(
                status='pending'
            )


class Sponsorship(db.Model):
    """Sponsorship model representing financial backing for an event."""
    __tablename__ = 'sponsorships'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, index=True)
    sponsor_name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    contact_email = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
