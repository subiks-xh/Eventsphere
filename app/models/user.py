"""
EventSphere - User Model
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager


class UserRole:
    """User roles for role-based access control."""
    ADMIN = 'admin'
    ORGANIZER = 'organizer'
    ATTENDEE = 'attendee'
    VENDOR = 'vendor'

    @classmethod
    def get_choices(cls):
        """Return role choices for forms."""
        return [
            (cls.ADMIN, 'Admin'),
            (cls.ORGANIZER, 'Organizer'),
            (cls.ATTENDEE, 'Attendee'),
            (cls.VENDOR, 'Vendor')
        ]


class UserStatus:
    """User account status."""
    ACTIVE = 'active'
    DISABLED = 'disabled'


class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, default=UserRole.ATTENDEE, index=True)
    status = db.Column(db.String(20), nullable=False, default=UserStatus.ACTIVE)
    profile_image = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organized_events = db.relationship('Event', foreign_keys='Event.organizer_id', backref='organizer', lazy=True)
    registrations = db.relationship('Registration', backref='user', foreign_keys='Registration.user_id', lazy=True)
    waitlist_entries = db.relationship('Waitlist', backref='user', foreign_keys='Waitlist.user_id', lazy=True)
    notifications = db.relationship('Notification', backref='user', foreign_keys='Notification.user_id', lazy=True)
    feedbacks = db.relationship('Feedback', backref='user', foreign_keys='Feedback.user_id', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='user', foreign_keys='AuditLog.user_id', lazy=True)
    vendor_profile = db.relationship('Vendor', backref='user', uselist=False, foreign_keys='Vendor.user_id')

    def __init__(self, username, email, password, role=UserRole.ATTENDEE, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
        self.status = UserStatus.ACTIVE

    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        """Get full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def is_active(self):
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE

    @property
    def is_admin(self):
        """Check if user is admin."""
        return self.role == UserRole.ADMIN

    @property
    def is_organizer(self):
        """Check if user is organizer."""
        return self.role == UserRole.ORGANIZER

    @property
    def is_attendee(self):
        """Check if user is attendee."""
        return self.role == UserRole.ATTENDEE

    @property
    def is_vendor(self):
        """Check if user is vendor."""
        return self.role == UserRole.VENDOR

    def get_id(self):
        """Get user ID for Flask-Login."""
        return str(self.id)

    @property
    def unread_notifications(self):
        """Get count of unread notifications."""
        from app.models.notification import Notification
        return Notification.query.filter_by(
            user_id=self.id, is_read=False
        ).count()

    @property
    def attended_events_count(self):
        """Get count of events attended."""
        from app.models.attendance import Attendance
        from app.models.registration import Registration
        return Attendance.query.join(Registration).filter(
            Registration.user_id == self.id
        ).count()

    @property
    def feedback_count(self):
        """Get count of feedback submitted."""
        from app.models.feedback import Feedback
        return Feedback.query.filter_by(user_id=self.id).count()

    @property
    def badges(self):
        """Compute gamification badges for this user."""
        from app.utils.badges import compute_badges
        return compute_badges(self)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

    def __str__(self):
        return self.full_name


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader."""
    return User.query.get(int(user_id))
