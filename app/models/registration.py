"""
EventSphere - Registration Model
"""

from datetime import datetime
from app import db


class RegistrationStatus:
    """Registration statuses."""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'

    @classmethod
    def get_choices(cls):
        """Return status choices for forms."""
        return [
            (cls.PENDING, 'Pending'),
            (cls.CONFIRMED, 'Confirmed'),
            (cls.CANCELLED, 'Cancelled')
        ]


class Registration(db.Model):
    """Registration model representing an attendee's registration for an event."""
    __tablename__ = 'registrations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default=RegistrationStatus.PENDING, index=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    special_requirements = db.Column(db.Text)
    reminder_sent = db.Column(db.Boolean, default=False, server_default='0', nullable=False)

    # Relationships
    ticket = db.relationship('Ticket', backref='registration', uselist=False, foreign_keys='Ticket.registration_id', cascade='all, delete-orphan')
    attendance = db.relationship('Attendance', backref='registration', uselist=False, foreign_keys='Attendance.registration_id', cascade='all, delete-orphan')
    certificate = db.relationship('Certificate', backref='registration', uselist=False, foreign_keys='Certificate.registration_id', cascade='all, delete-orphan')
    feedback = db.relationship('Feedback', backref='registration', uselist=False, foreign_keys='Feedback.registration_id', cascade='all, delete-orphan')

    # Unique constraint: one registration per user per event
    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='unique_registration'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.status:
            self.status = RegistrationStatus.PENDING

    @property
    def is_confirmed(self):
        """Check if the registration is confirmed."""
        return self.status == RegistrationStatus.CONFIRMED

    @property
    def is_cancelled(self):
        """Check if the registration is cancelled."""
        return self.status == RegistrationStatus.CANCELLED

    @property
    def has_ticket(self):
        """Check if a ticket has been generated."""
        return self.ticket is not None

    @property
    def has_checked_in(self):
        """Check if the attendee has checked in."""
        return self.attendance is not None

    @property
    def is_certificate_eligible(self):
        """Check if the attendee is eligible for a certificate."""
        if not self.has_checked_in:
            return False
        if self.event.status != 'completed':
            return False
        return True

    def cancel(self):
        """Cancel this registration."""
        self.status = RegistrationStatus.CANCELLED
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def confirm(self):
        """Confirm this registration."""
        self.status = RegistrationStatus.CONFIRMED
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f"<Registration {self.id} - {self.user.username if self.user else 'Unknown'} -> {self.event.name if self.event else 'Unknown'}>"
