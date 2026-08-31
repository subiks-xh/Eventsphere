"""
EventSphere - Waitlist Model
"""

from datetime import datetime
from app import db


class WaitlistStatus:
    """Waitlist statuses."""
    ACTIVE = 'active'
    PROMOTED = 'promoted'
    CANCELLED = 'cancelled'

    @classmethod
    def get_choices(cls):
        """Return status choices for forms."""
        return [
            (cls.ACTIVE, 'Active'),
            (cls.PROMOTED, 'Promoted'),
            (cls.CANCELLED, 'Cancelled')
        ]


class Waitlist(db.Model):
    """Waitlist model representing users waiting for event registration."""
    __tablename__ = 'waitlist'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default=WaitlistStatus.ACTIVE)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: one waitlist entry per user per event
    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='unique_waitlist'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.status:
            self.status = WaitlistStatus.ACTIVE

    @property
    def is_active(self):
        """Check if the waitlist entry is active."""
        return self.status == WaitlistStatus.ACTIVE

    @property
    def is_promoted(self):
        """Check if the waitlist entry has been promoted."""
        return self.status == WaitlistStatus.PROMOTED

    def promote(self):
        """Mark this waitlist entry as promoted."""
        self.status = WaitlistStatus.PROMOTED
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def cancel(self):
        """Cancel this waitlist entry."""
        self.status = WaitlistStatus.CANCELLED
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f"<Waitlist {self.id} - Position {self.position} for {self.user.username if self.user else 'Unknown'}>"
