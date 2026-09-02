"""
EventSphere - Main Routes
"""

from datetime import datetime

from flask import Blueprint, render_template
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page route."""
    if current_user.is_authenticated:
        # Redirect to appropriate dashboard based on role
        if current_user.is_admin:
            from flask import redirect, url_for
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_organizer:
            from flask import redirect, url_for
            return redirect(url_for('organizer.dashboard'))
        elif current_user.is_attendee:
            from flask import redirect, url_for
            return redirect(url_for('attendee.dashboard'))
        elif current_user.is_vendor:
            from flask import redirect, url_for
            return redirect(url_for('vendor.dashboard'))
    
    # Show public home page
    from app.models.event import Event, EventStatus
    upcoming_events = Event.query.filter(
        Event.status.in_([EventStatus.PUBLISHED, EventStatus.REGISTRATION_OPEN]),
        Event.date >= datetime.utcnow().date()
    ).order_by(Event.date, Event.start_time).limit(6).all()
    
    return render_template('main/index.html', events=upcoming_events)


@main_bp.route('/about')
def about():
    """About page."""
    return render_template('main/about.html')
