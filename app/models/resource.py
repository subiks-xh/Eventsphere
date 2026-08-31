"""
EventSphere - Resource Model
"""

from datetime import datetime
from app import db


class Resource(db.Model):
    """Resource model representing equipment and facilities."""
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    total_quantity = db.Column(db.Integer, nullable=False, default=1)
    available_quantity = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(50), nullable=False, default='available')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event_assignments = db.relationship('EventResource', backref='resource', foreign_keys='EventResource.resource_id', lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.available_quantity:
            self.available_quantity = self.total_quantity or 1
        if not self.status:
            self.status = 'available'

    @property
    def is_available(self):
        """Check if the resource is available."""
        return self.available_quantity > 0

    @property
    def utilization_percentage(self):
        """Get the utilization percentage."""
        if self.total_quantity == 0:
            return 0.0
        return ((self.total_quantity - self.available_quantity) / self.total_quantity) * 100

    def assign(self, quantity=1):
        """
        Assign a quantity of this resource.
        
        Args:
            quantity: Quantity to assign
        
        Returns:
            bool: True if successful, False if not enough available
        """
        if quantity > self.available_quantity:
            return False
        self.available_quantity -= quantity
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return True

    def release(self, quantity=1):
        """
        Release a quantity of this resource.
        
        Args:
            quantity: Quantity to release
        """
        self.available_quantity = min(self.available_quantity + quantity, self.total_quantity)
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f"<Resource {self.name} ({self.available_quantity}/{self.total_quantity})>"
