"""
EventSphere - Organizer Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, date
from app import db
from app.models.event import Event, EventStatus
from app.models.venue import Venue
from app.models.registration import Registration
from app.models.waitlist import Waitlist
from app.models.vendor import Vendor
from app.models.resource import Resource
from app.models.event_vendor import EventVendor
from app.models.event_resource import EventResource
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.models.feedback import Feedback
from app.models.notification import Notification, NotificationType
from app.models.audit_log import AuditLog
from app.models.user import UserRole

organizer_bp = Blueprint('organizer', __name__, template_folder='../templates/organizer', url_prefix='/organizer')


@organizer_bp.before_request
@login_required
def check_organizer():
    """Ensure only organizer or admin can access organizer routes."""
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        from flask import abort
        abort(403)


@organizer_bp.route('/')
@organizer_bp.route('/dashboard')
def dashboard():
    """Organizer dashboard."""
    # My events
    my_events = Event.query.filter_by(organizer_id=current_user.id).order_by(Event.date.desc()).limit(5).all()
    
    # Statistics
    total_events = Event.query.filter_by(organizer_id=current_user.id).count()
    total_registrations = Registration.query.join(Event).filter(
        Event.organizer_id == current_user.id
    ).count()
    total_attendance = Attendance.query.join(Registration).join(Event).filter(
        Event.organizer_id == current_user.id
    ).count()
    
    # Upcoming events
    upcoming_events = Event.query.filter(
        Event.organizer_id == current_user.id,
        Event.date >= date.today(),
        Event.status.in_([EventStatus.PUBLISHED, EventStatus.REGISTRATION_OPEN])
    ).order_by(Event.date).limit(5).all()
    
    # Events with high waitlist
    high_waitlist_events = Event.query.filter(
        Event.organizer_id == current_user.id
    ).order_by(Event.waitlist_count.desc()).limit(3).all()
    
    # Recent registrations
    recent_registrations = Registration.query.join(Event).filter(
        Event.organizer_id == current_user.id
    ).order_by(Registration.registration_date.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                          my_events=my_events,
                          total_events=total_events,
                          total_registrations=total_registrations,
                          total_attendance=total_attendance,
                          upcoming_events=upcoming_events,
                          high_waitlist_events=high_waitlist_events,
                          recent_registrations=recent_registrations,
                          title='Organizer Dashboard')


@organizer_bp.route('/events')
def my_events():
    """List organizer's events."""
    events = Event.query.filter_by(organizer_id=current_user.id).order_by(Event.date.desc()).all()
    return render_template('events/index.html', events=events, title='My Events')


@organizer_bp.route('/events/<int:event_id>/registrations')
def event_registrations(event_id):
    """View registrations for an event."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is organizer of this event or admin
    if current_user.id != event.organizer_id and not current_user.is_admin:
        from flask import abort
        abort(403)
    
    registrations = Registration.query.filter_by(event_id=event_id).order_by(Registration.registration_date.desc()).all()
    waitlist = Waitlist.query.filter_by(event_id=event_id).order_by(Waitlist.position).all()
    
    return render_template('events/registrations.html', 
                          event=event,
                          registrations=registrations,
                          waitlist=waitlist,
                          title=f'Registrations for {event.name}')


@organizer_bp.route('/events/<int:event_id>/checkin', methods=['GET', 'POST'])
def checkin(event_id):
    """Check in attendees for an event."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is organizer of this event or admin
    if current_user.id != event.organizer_id and not current_user.is_admin:
        from flask import abort
        abort(403)
    
    if request.method == 'POST':
        ticket_id = request.form.get('ticket_id')
        
        if not ticket_id:
            flash('Please enter a ticket ID.', 'error')
            return redirect(url_for('organizer.checkin', event_id=event.id))
        
        # Find registration by ticket
        ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
        
        if not ticket:
            flash('Ticket not found. Please check the ticket ID.', 'error')
            return redirect(url_for('organizer.checkin', event_id=event.id))
        
        if ticket.registration.event_id != event.id:
            flash('This ticket is not for this event.', 'error')
            return redirect(url_for('organizer.checkin', event_id=event.id))
        
        # Check if already checked in
        if ticket.registration.has_checked_in:
            flash('This attendee has already checked in.', 'error')
            return redirect(url_for('organizer.checkin', event_id=event.id))
        
        # Create attendance record
        attendance = Attendance(
            registration_id=ticket.registration.id,
            check_in_time=datetime.utcnow(),
            check_in_method='manual'
        )
        db.session.add(attendance)
        db.session.commit()
        
        # Create notification
        notification = Notification(
            user_id=ticket.registration.user_id,
            message=f'You have been checked in for "{event.name}".',
            type=NotificationType.CHECKIN,
            data={'event_id': event.id, 'attendance_id': attendance.id}
        )
        db.session.add(notification)
        db.session.commit()
        
        # Log action
        AuditLog.log_action(
            user_id=current_user.id,
            action='checkin',
            entity='attendance',
            entity_id=attendance.id,
            details=f"User {current_user.username} checked in {ticket.registration.user.username} for event {event.name}",
            request=request
        )
        
        flash(f'{ticket.registration.user.full_name} has been checked in!', 'success')
        return redirect(url_for('organizer.checkin', event_id=event.id))
    
    # Get checked-in attendees
    checked_in = Attendance.query.join(Registration).filter(
        Registration.event_id == event_id
    ).order_by(Attendance.check_in_time.desc()).all()
    
    return render_template('events/checkin.html', 
                          event=event,
                          checked_in=checked_in,
                          title=f'Check-in for {event.name}')


@organizer_bp.route('/events/<int:event_id>/certificates')
def event_certificates(event_id):
    """View and manage certificates for an event."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is organizer of this event or admin
    if current_user.id != event.organizer_id and not current_user.is_admin:
        from flask import abort
        abort(403)
    
    # Get eligible attendees (checked in and event completed)
    eligible_registrations = Registration.query.filter(
        Registration.event_id == event_id,
        Registration.has_checked_in == True
    ).all()
    
    # Get certificates
    certificates = Certificate.query.join(Registration).filter(
        Registration.event_id == event_id
    ).all()
    
    return render_template('events/certificates.html',
                          event=event,
                          eligible_registrations=eligible_registrations,
                          certificates=certificates,
                          title=f'Certificates for {event.name}')


@organizer_bp.route('/events/<int:event_id>/certificates/generate', methods=['POST'])
def generate_certificates(event_id):
    """Generate certificates for eligible attendees."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is organizer of this event or admin
    if current_user.id != event.organizer_id and not current_user.is_admin:
        from flask import abort
        abort(403)
    
    # Get eligible attendees
    eligible_registrations = Registration.query.filter(
        Registration.event_id == event_id,
        Registration.has_checked_in == True
    ).all()
    
    generated_count = 0
    for registration in eligible_registrations:
        # Check if certificate already exists
        existing_cert = Certificate.query.filter_by(registration_id=registration.id).first()
        if existing_cert:
            continue
        
        # Create certificate
        cert = Certificate(registration)
        db.session.add(cert)
        db.session.commit()
        
        # Generate PDF
        upload_path = current_user._get_current_object().app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
        cert_path = os.path.join(upload_path, 'certificates', f'certificate_{cert.id}.pdf')
        cert.generate_pdf(cert_path)
        
        # Create notification
        notification = Notification(
            user_id=registration.user_id,
            message=f'Your certificate for "{event.name}" is now available!',
            type=NotificationType.CERTIFICATE_AVAILABLE,
            data={'event_id': event.id, 'certificate_id': cert.id}
        )
        db.session.add(notification)
        db.session.commit()
        
        generated_count += 1
    
    # Log action
    AuditLog.log_action(
        user_id=current_user.id,
        action='generate_certificates',
        entity='certificate',
        entity_id=event_id,
        details=f"User {current_user.username} generated {generated_count} certificates for event {event.name}",
        request=request
    )
    
    flash(f'Generated certificates for {generated_count} eligible attendees!', 'success')
    return redirect(url_for('organizer.event_certificates', event_id=event.id))


@organizer_bp.route('/events/<int:event_id>/vendors')
def event_vendors(event_id):
    """Manage vendors for an event."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is organizer of this event or admin
    if current_user.id != event.organizer_id and not current_user.is_admin:
        from flask import abort
        abort(403)
    
    # Get all vendors
    all_vendors = Vendor.query.order_by(Vendor.business_name).all()
    
    # Get assigned vendors
    assigned_vendors = EventVendor.query.filter_by(event_id=event_id).all()
    
    return render_template('events/vendors.html',
                          event=event,
                          all_vendors=all_vendors,
                          assigned_vendors=assigned_vendors,
                          title=f'Vendors for {event.name}')


@organizer_bp.route('/events/<int:event_id>/vendors/add', methods=['POST'])
def add_vendor(event_id):
    """Add a vendor to an event."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is organizer of this event or admin
    if current_user.id != event.organizer_id and not current_user.is_admin:
        from flask import abort
        abort(403)
    
    vendor_id = request.form.get('vendor_id')
    service = request.form.get('service')
    
    if not vendor_id or not service:
        flash('Please select a vendor and service.', 'error')
        return redirect(url_for('organizer.event_vendors', event_id=event.id))
    
    # Check if already assigned
    existing = EventVendor.query.filter(
        EventVendor.event_id == event_id,
        EventVendor.vendor_id == vendor_id,
        EventVendor.service == service
    ).first()
    
    if existing:
        flash('This vendor is already assigned for this service.', 'error')
        return redirect(url_for('organizer.event_vendors', event_id=event.id))
    
    # Create assignment
    assignment = EventVendor(
        event_id=event_id,
        vendor_id=vendor_id,
        service=service,
        status='pending'
    )
    db.session.add(assignment)
    db.session.commit()
    
    # Log action
    AuditLog.log_action(
        user_id=current_user.id,
        action='assign_vendor',
        entity='event_vendor',
        entity_id=assignment.id,
        details=f"User {current_user.username} assigned vendor to event {event.name}",
        request=request
    )
    
    flash('Vendor assigned successfully!', 'success')
    return redirect(url_for('organizer.event_vendors', event_id=event.id))


@organizer_bp.route('/events/<int:event_id>/vendors/<int:assignment_id>/remove', methods=['POST'])
def remove_vendor(event_id, assignment_id):
    """Remove a vendor from an event."""
    assignment = EventVendor.query.get_or_404(assignment_id)
    
    # Check if user is organizer of this event or admin
    if current_user.id != assignment.event.organizer_id and not current_user.is_admin:
        from flask import abort
        abort(403)
    
    db.session.delete(assignment)
    db.session.commit()
    
    # Log action
    AuditLog.log_action(
        user_id=current_user.id,
        action='remove_vendor',
        entity='event_vendor',
        entity_id=assignment_id,
        details=f"User {current_user.username} removed vendor from event {assignment.event.name}",
        request=request
    )
    
    flash('Vendor removed successfully!', 'success')
    return redirect(url_for('organizer.event_vendors', event_id=event_id))


@organizer_bp.route('/events/<int:event_id>/resources')
def event_resources(event_id):
    """Manage resources for an event."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is organizer of this event or admin
    if current_user.id != event.organizer_id and not current_user.is_admin:
        from flask import abort
        abort(403)
    
    # Get all resources
    all_resources = Resource.query.order_by(Resource.name).all()
    
    # Get assigned resources
    assigned_resources = EventResource.query.filter_by(event_id=event_id).all()
    
    return render_template('events/resources.html',
                          event=event,
                          all_resources=all_resources,
                          assigned_resources=assigned_resources,
                          title=f'Resources for {event.name}')


@organizer_bp.route('/events/<int:event_id>/resources/add', methods=['POST'])
def add_resource(event_id):
    """Add a resource to an event."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is organizer of this event or admin
    if current_user.id != event.organizer_id and not current_user.is_admin:
        from flask import abort
        abort(403)
    
    resource_id = request.form.get('resource_id')
    quantity = request.form.get('quantity', 1, type=int)
    
    if not resource_id:
        flash('Please select a resource.', 'error')
        return redirect(url_for('organizer.event_resources', event_id=event.id))
    
    resource = Resource.query.get(resource_id)
    if not resource:
        flash('Resource not found.', 'error')
        return redirect(url_for('organizer.event_resources', event_id=event.id))
    
    # Check if already assigned
    existing = EventResource.query.filter(
        EventResource.event_id == event_id,
        EventResource.resource_id == resource_id
    ).first()
    
    if existing:
        # Update quantity
        existing.quantity += quantity
        db.session.commit()
        flash('Resource quantity updated!', 'success')
    else:
        # Check if enough available
        if quantity > resource.available_quantity:
            flash(f'Not enough {resource.name} available. Only {resource.available_quantity} remaining.', 'error')
            return redirect(url_for('organizer.event_resources', event_id=event.id))
        
        # Create assignment
        assignment = EventResource(
            event_id=event_id,
            resource_id=resource_id,
            quantity=quantity
        )
        db.session.add(assignment)
        
        # Update resource availability
        resource.assign(quantity)
        
        db.session.commit()
        
        flash('Resource assigned successfully!', 'success')
    
    # Log action
    AuditLog.log_action(
        user_id=current_user.id,
        action='assign_resource',
        entity='event_resource',
        entity_id=assignment.id,
        details=f"User {current_user.username} assigned resource to event {event.name}",
        request=request
    )
    
    return redirect(url_for('organizer.event_resources', event_id=event.id))


@organizer_bp.route('/events/<int:event_id>/announce', methods=['GET', 'POST'])
def announce(event_id):
    """Send announcement to event attendees."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is organizer of this event or admin
    if current_user.id != event.organizer_id and not current_user.is_admin:
        from flask import abort
        abort(403)
    
    if request.method == 'POST':
        message = request.form.get('message')
        
        if not message:
            flash('Please enter an announcement message.', 'error')
            return redirect(url_for('organizer.announce', event_id=event.id))
        
        # Get all registered users
        registrations = Registration.query.filter_by(event_id=event_id).all()
        
        for reg in registrations:
            notification = Notification(
                user_id=reg.user_id,
                message=f'Announcement for "{event.name}": {message}',
                type=NotificationType.ANNOUNCEMENT,
                data={'event_id': event.id, 'message': message}
            )
            db.session.add(notification)
        
        db.session.commit()
        
        # Log action
        AuditLog.log_action(
            user_id=current_user.id,
            action='announce',
            entity='event',
            entity_id=event.id,
            details=f"User {current_user.username} sent announcement to {len(registrations)} attendees",
            request=request
        )
        
        flash(f'Announcement sent to {len(registrations)} attendees!', 'success')
        return redirect(url_for('organizer.announce', event_id=event.id))
    
    return render_template('events/announce.html', event=event, title=f'Announce to {event.name}')
