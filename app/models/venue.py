"""
EventSphere - Venue Model
"""

from datetime import datetime
from app import db


class Venue(db.Model):
    """Venue model representing event locations."""
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text)
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    status = db.Column(db.String(20), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    events = db.relationship('Event', backref='venue', foreign_keys='Event.venue_id', lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.status:
            self.status = 'active'
        if not self.capacity:
            self.capacity = 0

    @property
    def full_address(self):
        """Get full formatted address."""
        parts = [self.address]
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country:
            parts.append(self.country)
        return ', '.join(parts)

    @property
    def event_count(self):
        """Get number of events at this venue."""
        return len(self.events) if self.events else 0

    @property
    def is_available(self):
        """Check if venue is available (not disabled)."""
        return self.status == 'active'

    def get_events(self):
        """Get all events at this venue, ordered by date."""
        return Event.query.filter_by(venue_id=self.id).order_by(Event.date, Event.start_time).all()

    def has_conflict(self, new_event):
        """
        Check if a new event conflicts with existing events at this venue.
        
        Args:
            new_event: Event object to check
        
        Returns:
            bool: True if conflict exists, False otherwise
        """
        if not new_event.date or not new_event.start_time or not new_event.end_time:
            return False

        from app.models.event import Event
        
        existing_events = Event.query.filter(
            Event.venue_id == self.id,
            Event.id != new_event.id
        ).all()

        new_start = datetime.combine(new_event.date, new_event.start_time)
        new_end = datetime.combine(new_event.date, new_event.end_time)

        for event in existing_events:
            if not event.date or not event.start_time or not event.end_time:
                continue

            existing_start = datetime.combine(event.date, event.start_time)
            existing_end = datetime.combine(event.date, event.end_time)

            # Check for overlap
            if new_start < existing_end and new_end > existing_start:
                return True

        return False

    def get_conflicting_events(self, new_event):
        """
        Get list of events that conflict with a new event.
        
        Args:
            new_event: Event object to check
        
        Returns:
            list: List of conflicting Event objects
        """
        if not new_event.date or not new_event.start_time or not new_event.end_time:
            return []

        from app.models.event import Event
        
        new_start = datetime.combine(new_event.date, new_event.start_time)
        new_end = datetime.combine(new_event.date, new_event.end_time)

        existing_events = Event.query.filter(
            Event.venue_id == self.id,
            Event.id != new_event.id
        ).all()

        conflicts = []
        for event in existing_events:
            if not event.date or not event.start_time or not event.end_time:
                continue

            existing_start = datetime.combine(event.date, event.start_time)
            existing_end = datetime.combine(event.date, event.end_time)

            if new_start < existing_end and new_end > existing_start:
                conflicts.append(event)

        return conflicts

    def __repr__(self):
        return f"<Venue {self.name} ({self.city})>"

    def __str__(self):
        return self.name
