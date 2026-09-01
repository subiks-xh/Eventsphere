"""
EventSphere - Event Model
"""

from datetime import datetime, date, time
from app import db


class EventCategory:
    """Event categories."""
    WORKSHOP = 'workshop'
    SEMINAR = 'seminar'
    CONFERENCE = 'conference'
    HACKATHON = 'hackathon'
    CULTURAL = 'cultural'
    SPORTS = 'sports'
    TECHNICAL = 'technical'
    OTHER = 'other'

    @classmethod
    def get_choices(cls):
        """Return category choices for forms."""
        return [
            (cls.WORKSHOP, 'Workshop'),
            (cls.SEMINAR, 'Seminar'),
            (cls.CONFERENCE, 'Conference'),
            (cls.HACKATHON, 'Hackathon'),
            (cls.CULTURAL, 'Cultural'),
            (cls.SPORTS, 'Sports'),
            (cls.TECHNICAL, 'Technical'),
            (cls.OTHER, 'Other')
        ]


class EventStatus:
    """Event statuses."""
    DRAFT = 'draft'
    PUBLISHED = 'published'
    REGISTRATION_OPEN = 'registration_open'
    REGISTRATION_CLOSED = 'registration_closed'
    ONGOING = 'ongoing'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    @classmethod
    def get_choices(cls):
        """Return status choices for forms."""
        return [
            (cls.DRAFT, 'Draft'),
            (cls.PUBLISHED, 'Published'),
            (cls.REGISTRATION_OPEN, 'Registration Open'),
            (cls.REGISTRATION_CLOSED, 'Registration Closed'),
            (cls.ONGOING, 'Ongoing'),
            (cls.COMPLETED, 'Completed'),
            (cls.CANCELLED, 'Cancelled')
        ]


class Event(db.Model):
    """Event model representing an event in the system."""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False, default=EventCategory.OTHER)
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), index=True)
    capacity = db.Column(db.Integer, nullable=False, default=0)
    registration_deadline = db.Column(db.DateTime)
    status = db.Column(db.String(50), nullable=False, default=EventStatus.DRAFT, index=True)
    image = db.Column(db.String(256))
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    registrations = db.relationship('Registration', backref='event', foreign_keys='Registration.event_id', lazy=True, cascade='all, delete-orphan')
    waitlist = db.relationship('Waitlist', backref='event', foreign_keys='Waitlist.event_id', lazy=True, cascade='all, delete-orphan')
    vendors = db.relationship('EventVendor', backref='event', foreign_keys='EventVendor.event_id', lazy=True, cascade='all, delete-orphan')
    resources = db.relationship('EventResource', backref='event', foreign_keys='EventResource.event_id', lazy=True, cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='event', foreign_keys='Feedback.event_id', lazy=True)
    budget = db.relationship('Budget', backref='event', uselist=False, lazy=True, cascade='all, delete-orphan')
    sponsorships = db.relationship('Sponsorship', backref='event', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.category:
            self.category = EventCategory.OTHER
        if not self.status:
            self.status = EventStatus.DRAFT
        if not self.capacity:
            self.capacity = 0

    @property
    def datetime(self):
        """Get event datetime (date + start_time)."""
        if self.date and self.start_time:
            return datetime.combine(self.date, self.start_time)
        return None

    @property
    def end_datetime(self):
        """Get event end datetime (date + end_time)."""
        if self.date and self.end_time:
            return datetime.combine(self.date, self.end_time)
        return None

    @property
    def duration(self):
        """Get event duration in hours."""
        if self.start_time and self.end_time:
            delta = datetime.combine(date.today(), self.end_time) - datetime.combine(date.today(), self.start_time)
            return delta.total_seconds() / 3600
        return 0

    @property
    def time_str(self):
        """Get formatted time string."""
        if self.start_time and self.end_time:
            return f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"
        return ""

    @property
    def is_published(self):
        """Check if the event is published."""
        return self.status in [EventStatus.PUBLISHED, EventStatus.REGISTRATION_OPEN]

    @property
    def is_registration_open(self):
        """Check if registration is currently open."""
        if self.status != EventStatus.REGISTRATION_OPEN:
            return False
        if self.registration_deadline:
            return datetime.utcnow() < self.registration_deadline
        return True

    @property
    def is_full(self):
        """Check if the event has reached capacity."""
        if self.capacity <= 0:
            return False
        confirmed_count = Registration.query.filter(
            Registration.event_id == self.id,
            Registration.status == 'confirmed'
        ).count()
        return confirmed_count >= self.capacity

    @property
    def confirmed_registrations_count(self):
        """Get the count of confirmed registrations."""
        return Registration.query.filter(
            Registration.event_id == self.id,
            Registration.status == 'confirmed'
        ).count()

    @property
    def waitlist_count(self):
        """Get the count of users on the waitlist."""
        return Waitlist.query.filter(
            Waitlist.event_id == self.id,
            Waitlist.status == 'active'
        ).count()

    @property
    def attendance_count(self):
        """Get the count of attendees who checked in."""
        return Attendance.query.join(Registration).filter(
            Registration.event_id == self.id
        ).count()

    @property
    def attendance_percentage(self):
        """Get the attendance percentage."""
        confirmed = self.confirmed_registrations_count
        if confirmed == 0:
            return 0.0
        return (self.attendance_count / confirmed) * 100

    @property
    def no_show_count(self):
        """Get the count of no-shows."""
        confirmed = self.confirmed_registrations_count
        return confirmed - self.attendance_count

    @property
    def no_show_percentage(self):
        """Get the no-show percentage."""
        confirmed = self.confirmed_registrations_count
        if confirmed == 0:
            return 0.0
        return (self.no_show_count / confirmed) * 100

    def can_register(self, user_id=None):
        """
        Check if a user can register for this event.
        
        Args:
            user_id: Optional user ID to check for existing registration
        
        Returns:
            tuple: (can_register: bool, reason: str)
        """
        # Check if event allows registration
        if self.status != EventStatus.REGISTRATION_OPEN:
            return False, "Registration is not open for this event"
        
        # Check if registration deadline has passed
        if self.registration_deadline and datetime.utcnow() > self.registration_deadline:
            return False, "Registration deadline has passed"
        
        # Check if event is cancelled
        if self.status == EventStatus.CANCELLED:
            return False, "This event has been cancelled"
        
        # Check if user already registered
        if user_id:
            existing = Registration.query.filter(
                Registration.event_id == self.id,
                Registration.user_id == user_id
            ).first()
            if existing:
                return False, "You have already registered for this event"
        
        # Check if event is full
        if self.is_full:
            return False, "This event is full"
        
        return True, "You can register for this event"

    def get_waitlist_position(self, user_id):
        """
        Get the user's position on the waitlist.
        
        Args:
            user_id: User ID
        
        Returns:
            int: Position on waitlist (1-indexed) or 0 if not on waitlist
        """
        waitlist_entry = Waitlist.query.filter(
            Waitlist.event_id == self.id,
            Waitlist.user_id == user_id,
            Waitlist.status == 'active'
        ).first()
        
        if not waitlist_entry:
            return 0
        
        return waitlist_entry.position

    def has_venue_conflict(self):
        """
        Check if this event conflicts with other events at the same venue.
        
        Returns:
            tuple: (has_conflict: bool, conflicting_events: list)
        """
        if not self.venue_id:
            return False, []
        
        return self.venue.has_conflict(self), self.venue.get_conflicting_events(self)

    def __repr__(self):
        return f"<Event {self.name} ({self.status})>"

    def __str__(self):
        return self.name


# Import for properties that use these models
from app.models.registration import Registration
from app.models.waitlist import Waitlist
from app.models.attendance import Attendance
