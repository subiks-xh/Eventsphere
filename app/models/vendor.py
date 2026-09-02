"""
EventSphere - Vendor Model
"""

from datetime import datetime
from app import db


class VendorService:
    """Vendor service types."""
    CATERING = 'catering'
    DECORATION = 'decoration'
    PHOTOGRAPHY = 'photography'
    AUDIO_VISUAL = 'audio_visual'
    TRANSPORTATION = 'transportation'
    SECURITY = 'security'
    PRINTING = 'printing'
    OTHER = 'other'

    @classmethod
    def get_choices(cls):
        """Return service choices for forms."""
        return [
            (cls.CATERING, 'Catering'),
            (cls.DECORATION, 'Decoration'),
            (cls.PHOTOGRAPHY, 'Photography'),
            (cls.AUDIO_VISUAL, 'Audio/Visual'),
            (cls.TRANSPORTATION, 'Transportation'),
            (cls.SECURITY, 'Security'),
            (cls.PRINTING, 'Printing'),
            (cls.OTHER, 'Other')
        ]

    @classmethod
    def get_label(cls, service):
        """Get the display label for a service."""
        labels = {
            cls.CATERING: 'Catering',
            cls.DECORATION: 'Decoration',
            cls.PHOTOGRAPHY: 'Photography',
            cls.AUDIO_VISUAL: 'Audio/Visual',
            cls.TRANSPORTATION: 'Transportation',
            cls.SECURITY: 'Security',
            cls.PRINTING: 'Printing',
            cls.OTHER: 'Other'
        }
        return labels.get(service, service)


class Vendor(db.Model):
    """Vendor model representing service providers."""
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    business_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    service = db.Column(db.String(50), nullable=False, default=VendorService.OTHER)
    description = db.Column(db.Text)
    address = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event_assignments = db.relationship('EventVendor', backref='vendor', foreign_keys='EventVendor.vendor_id', lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.service:
            self.service = VendorService.OTHER
        if not self.status:
            self.status = 'active'

    @property
    def assigned_events(self):
        """Get all events this vendor is assigned to."""
        from app.models.event import Event
        from app.models.event_vendor import EventVendor
        return Event.query.join(EventVendor, EventVendor.event_id == Event.id).filter(
            EventVendor.vendor_id == self.id
        ).all()

    @property
    def assigned_events_count(self):
        """Get the count of assigned events."""
        return len(self.assigned_events)

    def __repr__(self):
        return f"<Vendor {self.business_name} ({self.service})>"

    def __str__(self):
        return self.business_name
