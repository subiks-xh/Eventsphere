"""
EventSphere - Event Resource Association Model
"""

from datetime import datetime
from app import db


class EventResource(db.Model):
    """Association model between events and resources."""
    __tablename__ = 'event_resources'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(50), nullable=False, default='assigned')
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.quantity:
            self.quantity = 1
        if not self.status:
            self.status = 'assigned'

    def __repr__(self):
        return f"<EventResource {self.event.name if self.event else 'Unknown'} -> {self.resource.name if self.resource else 'Unknown'} ({self.quantity})>"
