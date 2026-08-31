"""
EventSphere - Event Vendor Association Model
"""

from datetime import datetime
from app import db


class EventVendorStatus:
    """Event vendor assignment statuses."""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'

    @classmethod
    def get_choices(cls):
        """Return status choices for forms."""
        return [
            (cls.PENDING, 'Pending'),
            (cls.CONFIRMED, 'Confirmed'),
            (cls.CANCELLED, 'Cancelled'),
            (cls.COMPLETED, 'Completed')
        ]


class EventVendor(db.Model):
    """Association model between events and vendors."""
    __tablename__ = 'event_vendors'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    service = db.Column(db.String(50), nullable=False)
    requirements = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default=EventVendorStatus.PENDING)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: one vendor-service combination per event
    __table_args__ = (
        db.UniqueConstraint('event_id', 'vendor_id', 'service', name='unique_event_vendor_service'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.status:
            self.status = EventVendorStatus.PENDING
        if not self.service:
            self.service = 'other'

    @property
    def is_confirmed(self):
        """Check if the assignment is confirmed."""
        return self.status == EventVendorStatus.CONFIRMED

    def confirm(self):
        """Confirm this vendor assignment."""
        self.status = EventVendorStatus.CONFIRMED
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def cancel(self):
        """Cancel this vendor assignment."""
        self.status = EventVendorStatus.CANCELLED
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def complete(self):
        """Mark this vendor assignment as completed."""
        self.status = EventVendorStatus.COMPLETED
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f"<EventVendor {self.event.name if self.event else 'Unknown'} -> {self.vendor.business_name if self.vendor else 'Unknown'} ({self.service})>"
