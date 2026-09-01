"""
EventSphere - REST API (v1)
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.event import Event
from app.models.venue import Venue
from app.models.registration import Registration
from app.models.user import User, UserRole
from app.models.resource import Resource
from app.models.vendor import Vendor
from app.models.budget import Budget, Expense

api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

def error_response(message, status_code=400):
    """Return a standard JSON error envelope."""
    return jsonify({"error": message}), status_code

def paginate_query(query):
    """Helper to paginate a SQLAlchemy query."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Cap per_page to prevent abuse
    if per_page > 100:
        per_page = 100
        
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': pagination.items,
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
        'per_page': per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }

# ---------------------------------------------------------
# Notifications (Existing Polling Route)
# ---------------------------------------------------------
@api_v1_bp.route('/notifications/unread_count', methods=['GET'])
@login_required
def get_unread_notification_count():
    """Get the unread notification count for the current user."""
    from app.models.notification import Notification
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'unread_count': count}), 200


# ---------------------------------------------------------
# Events API
# ---------------------------------------------------------
@api_v1_bp.route('/events', methods=['GET'])
def get_events():
    """List events."""
    query = Event.query.order_by(Event.date)
    paginated = paginate_query(query)
    
    events_data = [{
        'id': e.id,
        'name': e.name,
        'category': e.category,
        'status': e.status,
        'date': e.date.isoformat() if e.date else None,
        'capacity': e.capacity
    } for e in paginated['items']]
    
    return jsonify({
        'events': events_data,
        'meta': {k: v for k, v in paginated.items() if k != 'items'}
    }), 200

@api_v1_bp.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get event details."""
    event = Event.query.get_or_404(event_id)
    return jsonify({
        'id': event.id,
        'name': event.name,
        'description': event.description,
        'category': event.category,
        'date': event.date.isoformat() if event.date else None,
        'capacity': event.capacity,
        'status': event.status
    }), 200

@api_v1_bp.route('/events', methods=['POST'])
@login_required
def create_event():
    """Create an event."""
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        return error_response("Unauthorized", 403)
        
    data = request.get_json()
    if not data or not data.get('name') or not data.get('date'):
        return error_response("Missing required fields: 'name', 'date'", 400)
        
    try:
        event = Event(
            name=data['name'],
            description=data.get('description', ''),
            category=data.get('category', 'other'),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(data.get('start_time', '09:00'), '%H:%M').time(),
            end_time=datetime.strptime(data.get('end_time', '17:00'), '%H:%M').time(),
            capacity=data.get('capacity', 0),
            organizer_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        return jsonify({'message': 'Event created', 'id': event.id}), 201
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 400)

@api_v1_bp.route('/events/<int:event_id>', methods=['PUT', 'DELETE'])
@login_required
def update_delete_event(event_id):
    """Update or delete an event."""
    event = Event.query.get_or_404(event_id)
    if current_user.id != event.organizer_id and not current_user.is_admin:
        return error_response("Unauthorized", 403)
        
    if request.method == 'DELETE':
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted'}), 200
        
    data = request.get_json()
    if not data:
        return error_response("No data provided", 400)
        
    try:
        if 'name' in data: event.name = data['name']
        if 'description' in data: event.description = data['description']
        if 'capacity' in data: event.capacity = data['capacity']
        db.session.commit()
        return jsonify({'message': 'Event updated'}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 400)

@api_v1_bp.route('/events/forecast', methods=['GET'])
@login_required
def forecast_event_attendance():
    """Get forecasted attendance for a planned event."""
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        return error_response("Unauthorized", 403)
        
    category = request.args.get('category')
    capacity = request.args.get('capacity', type=int)
    
    if not capacity:
        return error_response("Missing required parameter: capacity", 400)
        
    from app.utils.forecasting import AttendanceForecaster
    forecast = AttendanceForecaster.forecast_attendance(category, capacity, current_user.id)
    
    return jsonify({
        'forecast': forecast,
        'capacity': capacity,
        'category': category
    }), 200

# ---------------------------------------------------------
# Attendees (Registrations) API
# ---------------------------------------------------------
@api_v1_bp.route('/registrations', methods=['GET'])
@login_required
def get_registrations():
    """List registrations (for the current user, or all if admin)."""
    if current_user.is_admin:
        query = Registration.query
    else:
        query = Registration.query.filter_by(user_id=current_user.id)
        
    paginated = paginate_query(query.order_by(Registration.registration_date.desc()))
    
    data = [{
        'id': r.id,
        'event_id': r.event_id,
        'user_id': r.user_id,
        'status': r.status
    } for r in paginated['items']]
    
    return jsonify({
        'registrations': data,
        'meta': {k: v for k, v in paginated.items() if k != 'items'}
    }), 200

# ---------------------------------------------------------
# Resources API
# ---------------------------------------------------------
@api_v1_bp.route('/resources', methods=['GET'])
def get_resources():
    """List resources."""
    query = Resource.query.order_by(Resource.name)
    paginated = paginate_query(query)
    
    data = [{
        'id': r.id,
        'name': r.name,
        'category': r.category,
        'total_quantity': r.total_quantity,
        'available_quantity': r.available_quantity
    } for r in paginated['items']]
    
    return jsonify({'resources': data, 'meta': {k: v for k, v in paginated.items() if k != 'items'}}), 200

# ---------------------------------------------------------
# Vendors API
# ---------------------------------------------------------
@api_v1_bp.route('/vendors', methods=['GET'])
def get_vendors():
    """List vendors."""
    query = Vendor.query.order_by(Vendor.business_name)
    paginated = paginate_query(query)
    
    data = [{
        'id': v.id,
        'business_name': v.business_name,
        'service_type': v.service_type,
        'rating': v.rating
    } for v in paginated['items']]
    
    return jsonify({'vendors': data, 'meta': {k: v for k, v in paginated.items() if k != 'items'}}), 200

# ---------------------------------------------------------
# Budget API
# ---------------------------------------------------------
@api_v1_bp.route('/events/<int:event_id>/budget', methods=['GET'])
@login_required
def get_budget(event_id):
    """Get budget for an event."""
    event = Event.query.get_or_404(event_id)
    if current_user.id != event.organizer_id and not current_user.is_admin:
        return error_response("Unauthorized", 403)
        
    budget = event.budget
    if not budget:
        return error_response("No budget created for this event", 404)
        
    return jsonify({
        'id': budget.id,
        'total_amount': budget.total_amount,
        'approved_expenses': budget.approved_expenses_total,
        'remaining': budget.remaining_budget,
        'utilization_percentage': budget.utilization_percentage
    }), 200
