"""
EventSphere - Notification Model
"""

from datetime import datetime
from app import db


class NotificationType:
    """Notification types."""
    REGISTRATION = 'registration'
    TICKET = 'ticket'
    WAITLIST = 'waitlist'
    WAITLIST_PROMOTION = 'waitlist_promotion'
    REGISTRATION_CANCELLED = 'registration_cancelled'
    EVENT_UPDATED = 'event_updated'
    EVENT_CANCELLED = 'event_cancelled'
    CERTIFICATE_AVAILABLE = 'certificate_available'
    ANNOUNCEMENT = 'announcement'
    CHECKIN = 'checkin'
    FEEDBACK = 'feedback'

    @classmethod
    def get_choices(cls):
        """Return type choices for forms."""
        return [
            (cls.REGISTRATION, 'Registration'),
            (cls.TICKET, 'Ticket'),
            (cls.WAITLIST, 'Waitlist'),
            (cls.WAITLIST_PROMOTION, 'Waitlist Promotion'),
            (cls.REGISTRATION_CANCELLED, 'Registration Cancelled'),
            (cls.EVENT_UPDATED, 'Event Updated'),
            (cls.EVENT_CANCELLED, 'Event Cancelled'),
            (cls.CERTIFICATE_AVAILABLE, 'Certificate Available'),
            (cls.ANNOUNCEMENT, 'Announcement'),
            (cls.CHECKIN, 'Check-in'),
            (cls.FEEDBACK, 'Feedback')
        ]

    @classmethod
    def get_label(cls, type_name):
        """Get the display label for a type."""
        labels = {
            cls.REGISTRATION: 'Registration',
            cls.TICKET: 'Ticket Generated',
            cls.WAITLIST: 'Waitlist Joined',
            cls.WAITLIST_PROMOTION: 'Waitlist Promotion',
            cls.REGISTRATION_CANCELLED: 'Registration Cancelled',
            cls.EVENT_UPDATED: 'Event Updated',
            cls.EVENT_CANCELLED: 'Event Cancelled',
            cls.CERTIFICATE_AVAILABLE: 'Certificate Available',
            cls.ANNOUNCEMENT: 'Announcement',
            cls.CHECKIN: 'Checked In',
            cls.FEEDBACK: 'Feedback Received'
        }
        return labels.get(type_name, type_name)


class Notification(db.Model):
    """Notification model for in-app notifications."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    data = db.Column(db.JSON)  # Additional data (e.g., event_id, registration_id)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_read = False

    def mark_as_read(self):
        """Mark this notification as read."""
        self.is_read = True
        self.read_at = datetime.utcnow()
        db.session.commit()

    @property
    def type_label(self):
        """Get the type label."""
        return NotificationType.get_label(self.type)

    @property
    def time_ago(self):
        """Get the time since creation."""
        now = datetime.utcnow()
        delta = now - self.created_at

        if delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

    def __repr__(self):
        return f"<Notification {self.id} - {self.type} for user {self.user_id}>"
