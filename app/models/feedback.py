"""
EventSphere - Feedback Model
"""

from datetime import datetime
from app import db


class Feedback(db.Model):
    """Feedback model for post-event feedback collection."""
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registrations.id'), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comments = db.Column(db.Text)
    suggestions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def rating_stars(self):
        """Get the rating as star symbols."""
        full = '★' * self.rating
        empty = '☆' * (5 - self.rating)
        return full + empty

    @property
    def rating_label(self):
        """Get the rating label."""
        labels = {
            1: 'Poor',
            2: 'Fair',
            3: 'Good',
            4: 'Very Good',
            5: 'Excellent'
        }
        return labels.get(self.rating, str(self.rating))

    def __repr__(self):
        return f"<Feedback {self.id} - {self.rating}/5 for {self.event.name if self.event else 'Unknown'}>"
