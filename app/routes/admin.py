"""
EventSphere - Admin Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import User, UserRole
from app.models.event import Event
from app.models.venue import Venue
from app.models.registration import Registration
from app.models.vendor import Vendor
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app import db

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin', url_prefix='/admin')


@admin_bp.before_request
@login_required
def check_admin():
    """Ensure only admin can access admin routes."""
    if not current_user.is_admin:
        from flask import abort
        abort(403)


@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard."""
    # Statistics
    total_users = User.query.count()
    total_events = Event.query.count()
    total_venues = Venue.query.count()
    total_vendors = Vendor.query.count()
    total_registrations = Registration.query.count()
    total_attendees = User.query.filter_by(role=UserRole.ATTENDEE).count()
    total_organizers = User.query.filter_by(role=UserRole.ORGANIZER).count()
    
    # Recent events
    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    
    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Upcoming events
    from datetime import date
    upcoming_events = Event.query.filter(
        Event.date >= date.today(),
        Event.status.in_([Event.status.PUBLISHED, Event.status.REGISTRATION_OPEN])
    ).order_by(Event.date).limit(5).all()
    
    return render_template('dashboard.html',
                          total_users=total_users,
                          total_events=total_events,
                          total_venues=total_venues,
                          total_vendors=total_vendors,
                          total_registrations=total_registrations,
                          total_attendees=total_attendees,
                          total_organizers=total_organizers,
                          recent_events=recent_events,
                          recent_users=recent_users,
                          upcoming_events=upcoming_events,
                          title='Admin Dashboard')


@admin_bp.route('/users')
def users():
    """List all users."""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users/index.html', users=users, title='All Users')


@admin_bp.route('/users/<int:user_id>')
def user_detail(user_id):
    """View user details."""
    user = User.query.get_or_404(user_id)
    return render_template('users/detail.html', user=user, title=user.username)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
def toggle_user(user_id):
    """Toggle user status (active/disabled)."""
    user = User.query.get_or_404(user_id)
    
    if user.status == 'active':
        user.status = 'disabled'
        flash(f'User {user.username} has been disabled.', 'success')
    else:
        user.status = 'active'
        flash(f'User {user.username} has been enabled.', 'success')
    
    db.session.commit()
    return redirect(url_for('admin.users'))


@admin_bp.route('/audit-logs')
def audit_logs():
    """View audit logs."""
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return render_template('audit_logs.html', logs=logs, title='Audit Logs')


@admin_bp.route('/statistics')
def statistics():
    """View platform statistics."""
    from datetime import date, timedelta
    
    # User statistics by role
    role_stats = {}
    for role in UserRole.get_choices():
        role_stats[role[0]] = User.query.filter_by(role=role[0]).count()
    
    # Event statistics by category
    category_stats = {}
    for category in EventCategory.get_choices():
        category_stats[category[0]] = Event.query.filter_by(category=category[0]).count()
    
    # Event statistics by status
    status_stats = {}
    for status in EventStatus.get_choices():
        status_stats[status[0]] = Event.query.filter_by(status=status[0]).count()
    
    # Monthly registrations (last 6 months)
    monthly_registrations = []
    for i in range(6):
        month_start = date.today() - timedelta(days=30*(i+1))
        month_end = date.today() - timedelta(days=30*i)
        count = Registration.query.filter(
            Registration.registration_date >= datetime.combine(month_start, datetime.min.time()),
            Registration.registration_date <= datetime.combine(month_end, datetime.max.time())
        ).count()
        month_name = month_start.strftime('%b %Y')
        monthly_registrations.append({'month': month_name, 'count': count})
    
    return render_template('statistics.html',
                          role_stats=role_stats,
                          category_stats=category_stats,
                          status_stats=status_stats,
                          monthly_registrations=monthly_registrations,
                          title='Statistics')
