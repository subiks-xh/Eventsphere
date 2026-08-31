"""
EventSphere - Ticket Model
"""

from datetime import datetime
import uuid
import os
from app import db


class Ticket(db.Model):
    """Ticket model representing a digital ticket for an event registration."""
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registrations.id'), unique=True, nullable=False)
    ticket_id = db.Column(db.String(50), unique=True, nullable=False)
    attendee_name = db.Column(db.String(200), nullable=False)
    event_name = db.Column(db.String(200), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.String(100), nullable=False)
    venue_name = db.Column(db.String(200), nullable=False)
    qr_code_path = db.Column(db.String(256))
    qr_code_data = db.Column(db.String(100))  # Store ticket_id for QR
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, registration, **kwargs):
        """
        Initialize a new ticket for a registration.
        
        Args:
            registration: Registration object
            **kwargs: Additional ticket attributes
        """
        super().__init__(**kwargs)
        self.registration_id = registration.id
        self.ticket_id = f"TKT-{str(uuid.uuid4())[:8].upper()}"
        self.attendee_name = registration.user.full_name
        self.event_name = registration.event.name
        self.event_date = registration.event.date
        self.event_time = f"{registration.event.start_time.strftime('%H:%M')} - {registration.event.end_time.strftime('%H:%M')}"
        self.venue_name = registration.event.venue.name if registration.event.venue else "TBD"
        self.qr_code_data = self.ticket_id

    def generate_qr_code(self, save_path=None):
        """
        Generate QR code for this ticket.
        
        Args:
            save_path: Optional path to save the QR code image
        
        Returns:
            bytes: QR code image data
        """
        import qrcode
        import io

        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.qr_code_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        # Save to file if path provided
        if save_path:
            img.save(save_path)
            # Store relative path
            self.qr_code_path = os.path.relpath(save_path, 'app/static')
            db.session.commit()

        return img_bytes.getvalue()

    def get_qr_code_url(self):
        """Get URL for QR code image."""
        if self.qr_code_path:
            return f"/static/{self.qr_code_path}"
        return None

    def __repr__(self):
        return f"<Ticket {self.ticket_id} for {self.attendee_name}>"
