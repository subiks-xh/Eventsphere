"""
EventSphere - Admin Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app.models.user import User, UserRole
from app.models.event import Event, EventCategory, EventStatus
from app.models.venue import Venue
from app.models.registration import Registration
from app.models.attendance import Attendance
from app.models.vendor import Vendor
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app import db
import csv
import io

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


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
    upcoming_events = Event.query.filter(
        Event.date >= date.today(),
        Event.status.in_([EventStatus.PUBLISHED, EventStatus.REGISTRATION_OPEN])
    ).order_by(Event.date).limit(5).all()

    return render_template('admin/dashboard.html',
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
    """List all users with pagination."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    role_filter = request.args.get('role', '', type=str)

    query = User.query
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%'))
        )
    if role_filter:
        query = query.filter_by(role=role_filter)

    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)

    return render_template('admin/users/index.html',
                          users=pagination.items,
                          pagination=pagination,
                          search=search,
                          role_filter=role_filter,
                          title='All Users')


@admin_bp.route('/users/<int:user_id>')
def user_detail(user_id):
    """View user details."""
    user = User.query.get_or_404(user_id)
    return render_template('users/detail.html', user=user, title=user.username)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
def toggle_user(user_id):
    """Toggle user status (active/disabled)."""
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('You cannot disable your own account.', 'error')
        return redirect(url_for('admin.users'))

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
    """View audit logs with pagination."""
    page = request.args.get('page', 1, type=int)
    pagination = AuditLog.query.order_by(
        AuditLog.created_at.desc()
    ).paginate(page=page, per_page=50, error_out=False)

    return render_template('admin/audit_logs.html',
                          logs=pagination.items,
                          pagination=pagination,
                          title='Audit Logs')


@admin_bp.route('/statistics')
def statistics():
    """View platform statistics."""
    # User statistics by role
    role_stats = {}
    for role_val, role_label in UserRole.get_choices():
        role_stats[role_val] = User.query.filter_by(role=role_val).count()

    # Event statistics by category
    category_stats = {}
    for cat_val, cat_label in EventCategory.get_choices():
        category_stats[cat_label] = Event.query.filter_by(category=cat_val).count()

    # Event statistics by status
    status_stats = {}
    for status_val, status_label in EventStatus.get_choices():
        status_stats[status_label] = Event.query.filter_by(status=status_val).count()

    # Monthly registrations (last 6 months)
    monthly_registrations = []
    for i in range(5, -1, -1):
        month_start = date.today().replace(day=1) - timedelta(days=30 * i)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        count = Registration.query.filter(
            Registration.registration_date >= datetime.combine(month_start, datetime.min.time()),
            Registration.registration_date < datetime.combine(month_end, datetime.min.time())
        ).count()
        month_name = month_start.strftime('%b %Y')
        monthly_registrations.append({'month': month_name, 'count': count})

    # Overall metrics
    total_events = Event.query.count()
    completed_events = Event.query.filter_by(status=EventStatus.COMPLETED).count()
    upcoming_events = Event.query.filter(
        Event.date >= date.today(),
        Event.status.in_([EventStatus.PUBLISHED, EventStatus.REGISTRATION_OPEN])
    ).count()
    total_registrations = Registration.query.filter_by(status='confirmed').count()
    total_attendance = Attendance.query.count()
    confirmed_count = Registration.query.filter_by(status='confirmed').count()
    attendance_pct = round((total_attendance / confirmed_count * 100), 1) if confirmed_count > 0 else 0

    # Average feedback rating
    from app.models.feedback import Feedback
    from sqlalchemy import func
    avg_rating = db.session.query(func.avg(Feedback.rating)).scalar()
    avg_rating = round(float(avg_rating), 1) if avg_rating else 0

    return render_template('admin/statistics.html',
                          role_stats=role_stats,
                          category_stats=category_stats,
                          status_stats=status_stats,
                          monthly_registrations=monthly_registrations,
                          total_events=total_events,
                          completed_events=completed_events,
                          upcoming_events=upcoming_events,
                          total_registrations=total_registrations,
                          total_attendance=total_attendance,
                          attendance_pct=attendance_pct,
                          avg_rating=avg_rating,
                          title='Statistics')


@admin_bp.route('/export/users.csv')
def export_users_csv():
    """Export all users as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Username', 'Email', 'First Name', 'Last Name', 'Role', 'Status', 'Joined'])

    users = User.query.order_by(User.created_at).all()
    for user in users:
        writer.writerow([
            user.id, user.username, user.email,
            user.first_name or '', user.last_name or '',
            user.role, user.status,
            user.created_at.strftime('%Y-%m-%d')
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=users.csv'}
    )
