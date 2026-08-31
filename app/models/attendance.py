"""
EventSphere - Attendance Model
"""

from datetime import datetime
from app import db


class Attendance(db.Model):
    """Attendance model tracking event check-ins."""
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registrations.id'), unique=True, nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    check_in_method = db.Column(db.String(50), default='manual')  # manual, qr_code
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.check_in_method:
            self.check_in_method = 'manual'

    @property
    def check_in_date(self):
        """Get the check-in date."""
        return self.check_in_time.date() if self.check_in_time else None

    @property
    def check_in_time_str(self):
        """Get the check-in time as string."""
        return self.check_in_time.strftime('%H:%M:%S') if self.check_in_time else None

    def __repr__(self):
        return f"<Attendance {self.registration.user.username if self.registration and self.registration.user else 'Unknown'} at {self.check_in_time}>"
