"""
EventSphere - Routes Package
"""

from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.admin import admin_bp
from app.routes.organizer import organizer_bp
from app.routes.attendee import attendee_bp
from app.routes.vendor import vendor_bp
from app.routes.venue import venue_bp
from app.routes.events import events_bp
from app.routes.api import api_v1_bp
from app.routes.errors import errors_bp

__all__ = [
    'auth_bp', 'main_bp', 'admin_bp', 'organizer_bp', 'attendee_bp',
    'vendor_bp', 'venue_bp', 'events_bp', 'api_v1_bp', 'errors_bp'
]
