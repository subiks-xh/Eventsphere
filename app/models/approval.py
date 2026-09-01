"""
EventSphere - Approval Request Model
"""

from datetime import datetime
from app import db


class ApprovalStatus:
    """Approval statuses."""
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'


class ApprovalRequest(db.Model):
    """Generic approval request model for various entities (e.g., expenses)."""
    __tablename__ = 'approval_requests'

    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=True) # Optional link to an expense
    status = db.Column(db.String(50), nullable=False, default=ApprovalStatus.PENDING)
    
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    resolver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    resolver = db.relationship('User', foreign_keys=[resolver_id])
