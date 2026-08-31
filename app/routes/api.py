"""
EventSphere - API Routes
Simple REST API for EventSphere
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.event import Event
from app.models.venue import Venue
from app.models.registration import Registration
from app.models.user import UserRole

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/events', methods=['GET'])
def get_events():
    """Get list of all events."""
    events = Event.query.filter(
        Event.status.in_(['published', 'registration_open'])
    ).order_by(Event.date).all()
    
    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'name': event.name,
            'description': event.description,
            'category': event.category,
            'date': event.date.isoformat() if event.date else None,
            'start_time': event.start_time.isoformat() if event.start_time else None,
            'end_time': event.end_time.isoformat() if event.end_time else None,
            'venue': event.venue.name if event.venue else None,
            'capacity': event.capacity,
            'status': event.status,
            'organizer': event.organizer.username if event.organizer else None
        })
    
    return jsonify({'events': events_data})


@api_bp.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get event details."""
    event = Event.query.get_or_404(event_id)
    
    event_data = {
        'id': event.id,
        'name': event.name,
        'description': event.description,
        'category': event.category,
        'date': event.date.isoformat() if event.date else None,
        'start_time': event.start_time.isoformat() if event.start_time else None,
        'end_time': event.end_time.isoformat() if event.end_time else None,
        'venue': {
            'id': event.venue.id,
            'name': event.venue.name,
            'address': event.venue.full_address,
            'capacity': event.venue.capacity
        } if event.venue else None,
        'capacity': event.capacity,
        'registration_count': event.confirmed_registrations_count,
        'waitlist_count': event.waitlist_count,
        'status': event.status,
        'organizer': {
            'id': event.organizer.id,
            'username': event.organizer.username,
            'full_name': event.organizer.full_name
        } if event.organizer else None
    }
    
    return jsonify({'event': event_data})


@api_bp.route('/venues', methods=['GET'])
def get_venues():
    """Get list of all venues."""
    venues = Venue.query.order_by(Venue.name).all()
    
    venues_data = []
    for venue in venues:
        venues_data.append({
            'id': venue.id,
            'name': venue.name,
            'address': venue.full_address,
            'capacity': venue.capacity,
            'status': venue.status,
            'event_count': venue.event_count
        })
    
    return jsonify({'venues': venues_data})


@api_bp.route('/registrations', methods=['GET'])
@login_required
def get_registrations():
    """Get user's registrations."""
    registrations = Registration.query.filter_by(user_id=current_user.id).all()
    
    registrations_data = []
    for reg in registrations:
        registrations_data.append({
            'id': reg.id,
            'event_id': reg.event.id,
            'event_name': reg.event.name,
            'event_date': reg.event.date.isoformat() if reg.event.date else None,
            'status': reg.status,
            'registration_date': reg.registration_date.isoformat()
        })
    
    return jsonify({'registrations': registrations_data})
