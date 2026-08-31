"""
EventSphere - Event Routes
CRUD operations for events with venue conflict detection
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime, date
from app import db
from app.models.event import Event, EventCategory, EventStatus
from app.models.venue import Venue
from app.models.user import UserRole
from app.models.registration import Registration, RegistrationStatus
from app.models.waitlist import Waitlist, WaitlistStatus
from app.models.ticket import Ticket
from app.models.notification import Notification, NotificationType
from app.forms.event_forms import EventForm
from app.models.audit_log import AuditLog

events_bp = Blueprint('events', __name__, template_folder='../templates/events', url_prefix='/events')


@events_bp.before_request
@login_required
def check_organizer_or_admin():
    """Ensure only organizer or admin can access event management routes."""
    # Allow GET requests for public event viewing
    if request.method == 'GET' and not request.path.endswith(('create', 'edit', 'delete')):
        return
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        abort(403)


@events_bp.route('/')
def index():
    """List all events (public)."""
    # Public view - show published/registration_open events
    events = Event.query.filter(
        Event.status.in_([EventStatus.PUBLISHED, EventStatus.REGISTRATION_OPEN])
    ).order_by(Event.date, Event.start_time).all()
    
    return render_template('index.html', events=events, title='All Events')


@events_bp.route('/upcoming')
def upcoming():
    """List upcoming events."""
    today = date.today()
    events = Event.query.filter(
        Event.status.in_([EventStatus.PUBLISHED, EventStatus.REGISTRATION_OPEN]),
        Event.date >= today
    ).order_by(Event.date, Event.start_time).all()
    
    return render_template('upcoming.html', events=events, title='Upcoming Events')


@events_bp.route('/past')
def past():
    """List past events."""
    today = date.today()
    events = Event.query.filter(
        Event.date < today
    ).order_by(Event.date.desc(), Event.start_time.desc()).all()
    
    return render_template('past.html', events=events, title='Past Events')


@events_bp.route('/<int:event_id>')
def detail(event_id):
    """View event details."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is registered
    is_registered = False
    is_on_waitlist = False
    registration = None
    
    if current_user.is_authenticated:
        registration = Registration.query.filter(
            Registration.event_id == event_id,
            Registration.user_id == current_user.id
        ).first()
        
        if registration:
            is_registered = True
        else:
            waitlist_entry = Waitlist.query.filter(
                Waitlist.event_id == event_id,
                Waitlist.user_id == current_user.id,
                Waitlist.status == 'active'
            ).first()
            if waitlist_entry:
                is_on_waitlist = True
    
    # Get venue conflict info
    has_conflict, conflicting_events = event.has_venue_conflict()
    
    return render_template('detail.html', 
                          event=event, 
                          is_registered=is_registered,
                          is_on_waitlist=is_on_waitlist,
                          registration=registration,
                          has_conflict=has_conflict,
                          conflicting_events=conflicting_events,
                          title=event.name)


@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new event (organizer/admin only)."""
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        abort(403)
    
    form = EventForm()
    
    if form.validate_on_submit():
        # Check for venue conflict
        venue = Venue.query.get(form.venue_id.data)
        if venue:
            # Create temporary event to check conflict
            temp_event = Event(
                name=form.name.data,
                date=form.date.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                venue_id=form.venue_id.data
            )
            
            has_conflict, conflicting_events = venue.has_conflict(temp_event)
            
            if has_conflict:
                conflict_names = [e.name for e in conflicting_events]
                form.venue_id.errors.append(
                    f'Venue conflict! This venue already has events: {", ".join(conflict_names)}'
                )
                return render_template('create.html', form=form, title='Create Event')
        
        # Create the event
        event = Event(
            name=form.name.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            category=form.category.data,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            venue_id=form.venue_id.data,
            capacity=form.capacity.data or 0,
            registration_deadline=form.registration_deadline.data,
            status=form.status.data or EventStatus.DRAFT,
            image=form.image.data.strip() if form.image.data else None,
            organizer_id=current_user.id
        )
        
        db.session.add(event)
        db.session.commit()
        
        # Log creation action
        AuditLog.log_action(
            user_id=current_user.id,
            action='create',
            entity='event',
            entity_id=event.id,
            details=f"User {current_user.username} created event {event.name}",
            request=request
        )
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('events.detail', event_id=event.id))
    
    return render_template('create.html', form=form, title='Create Event')


@events_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    """Edit an event (organizer/admin only)."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is organizer of this event or admin
    if current_user.id != event.organizer_id and not current_user.is_admin:
        abort(403)
    
    form = EventForm(obj=event)
    
    if form.validate_on_submit():
        # Check for venue conflict (if venue changed or date/time changed)
        venue_changed = form.venue_id.data != event.venue_id
        date_changed = form.date.data != event.date
        time_changed = form.start_time.data != event.start_time or form.end_time.data != event.end_time
        
        if venue_changed or date_changed or time_changed:
            venue = Venue.query.get(form.venue_id.data)
            if venue:
                # Create temporary event to check conflict
                temp_event = Event(
                    id=event.id,  # Same ID so it excludes itself
                    name=form.name.data,
                    date=form.date.data,
                    start_time=form.start_time.data,
                    end_time=form.end_time.data,
                    venue_id=form.venue_id.data
                )
                
                has_conflict, conflicting_events = venue.has_conflict(temp_event)
                
                if has_conflict:
                    conflict_names = [e.name for e in conflicting_events if e.id != event.id]
                    if conflict_names:
                        form.venue_id.errors.append(
                            f'Venue conflict! This venue already has events: {", ".join(conflict_names)}'
                        )
                        return render_template('edit.html', form=form, event=event, title=f'Edit {event.name}')
        
        # Update the event
        event.name = form.name.data.strip()
        event.description = form.description.data.strip() if form.description.data else None
        event.category = form.category.data
        event.date = form.date.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.venue_id = form.venue_id.data
        event.capacity = form.capacity.data or 0
        event.registration_deadline = form.registration_deadline.data
        event.status = form.status.data or EventStatus.DRAFT
        event.image = form.image.data.strip() if form.image.data else None
        
        db.session.commit()
        
        # Log update action
        AuditLog.log_action(
            user_id=current_user.id,
            action='update',
            entity='event',
            entity_id=event.id,
            details=f"User {current_user.username} updated event {event.name}",
            request=request
        )
        
        # Notify registered users if date/time/venue changed
        if date_changed or time_changed or venue_changed:
            registrations = Registration.query.filter_by(event_id=event.id).all()
            for reg in registrations:
                notification = Notification(
                    user_id=reg.user_id,
                    message=f'Event "{event.name}" has been updated. Please check the new details.',
                    type=NotificationType.EVENT_UPDATED,
                    data={'event_id': event.id}
                )
                db.session.add(notification)
            db.session.commit()
        
        flash('Event updated successfully!', 'success')
        return redirect(url_for('events.detail', event_id=event.id))
    
    return render_template('edit.html', form=form, event=event, title=f'Edit {event.name}')


@events_bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete(event_id):
    """Delete an event (organizer/admin only)."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is organizer of this event or admin
    if current_user.id != event.organizer_id and not current_user.is_admin:
        abort(403)
    
    # Notify registered users
    registrations = Registration.query.filter_by(event_id=event.id).all()
    for reg in registrations:
        notification = Notification(
            user_id=reg.user_id,
            message=f'Event "{event.name}" has been cancelled.',
            type=NotificationType.EVENT_CANCELLED,
            data={'event_id': event.id}
        )
        db.session.add(notification)
    
    # Delete event
    db.session.delete(event)
    db.session.commit()
    
    # Log deletion action
    AuditLog.log_action(
        user_id=current_user.id,
        action='delete',
        entity='event',
        entity_id=event_id,
        details=f"User {current_user.username} deleted event {event.name}",
        request=request
    )
    
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('events.index'))


@events_bp.route('/<int:event_id>/publish', methods=['POST'])
@login_required
def publish(event_id):
    """Publish an event (organizer/admin only)."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is organizer of this event or admin
    if current_user.id != event.organizer_id and not current_user.is_admin:
        abort(403)
    
    # Check for venue conflict before publishing
    if event.venue_id:
        has_conflict, conflicting_events = event.has_venue_conflict()
        if has_conflict:
            flash('Cannot publish event with venue conflict!', 'error')
            return redirect(url_for('events.detail', event_id=event.id))
    
    # Publish the event
    event.status = EventStatus.REGISTRATION_OPEN
    db.session.commit()
    
    # Log action
    AuditLog.log_action(
        user_id=current_user.id,
        action='publish',
        entity='event',
        entity_id=event.id,
        details=f"User {current_user.username} published event {event.name}",
        request=request
    )
    
    flash('Event published successfully! Registration is now open.', 'success')
    return redirect(url_for('events.detail', event_id=event.id))


@events_bp.route('/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel(event_id):
    """Cancel an event (organizer/admin only)."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is organizer of this event or admin
    if current_user.id != event.organizer_id and not current_user.is_admin:
        abort(403)
    
    # Cancel the event
    event.status = EventStatus.CANCELLED
    db.session.commit()
    
    # Notify registered users
    registrations = Registration.query.filter_by(event_id=event.id).all()
    for reg in registrations:
        notification = Notification(
            user_id=reg.user_id,
            message=f'Event "{event.name}" has been cancelled. Your registration has been cancelled.',
            type=NotificationType.EVENT_CANCELLED,
            data={'event_id': event.id}
        )
        db.session.add(notification)
        reg.cancel()  # Cancel registration
    
    # Notify waitlisted users
    waitlist_entries = Waitlist.query.filter_by(event_id=event.id).all()
    for entry in waitlist_entries:
        notification = Notification(
            user_id=entry.user_id,
            message=f'Event "{event.name}" has been cancelled.',
            type=NotificationType.EVENT_CANCELLED,
            data={'event_id': event.id}
        )
        db.session.add(notification)
        entry.cancel()
    
    db.session.commit()
    
    # Log action
    AuditLog.log_action(
        user_id=current_user.id,
        action='cancel',
        entity='event',
        entity_id=event.id,
        details=f"User {current_user.username} cancelled event {event.name}",
        request=request
    )
    
    flash('Event cancelled successfully!', 'success')
    return redirect(url_for('events.detail', event_id=event.id))


@events_bp.route('/<int:event_id>/register', methods=['GET', 'POST'])
@login_required
def register(event_id):
    """Register for an event."""
    event = Event.query.get_or_404(event_id)
    
    # Check if registration is allowed
    can_register, reason = event.can_register(current_user.id)
    if not can_register:
        flash(reason, 'error')
        return redirect(url_for('events.detail', event_id=event.id))
    
    # Check if already registered or on waitlist
    existing_registration = Registration.query.filter(
        Registration.event_id == event_id,
        Registration.user_id == current_user.id
    ).first()
    
    if existing_registration:
        flash('You have already registered for this event.', 'error')
        return redirect(url_for('events.detail', event_id=event.id))
    
    existing_waitlist = Waitlist.query.filter(
        Waitlist.event_id == event_id,
        Waitlist.user_id == current_user.id,
        Waitlist.status == 'active'
    ).first()
    
    if existing_waitlist:
        flash('You are already on the waitlist for this event.', 'error')
        return redirect(url_for('events.detail', event_id=event.id))
    
    # Create registration
    if event.is_full:
        # Add to waitlist
        # Get next position
        last_position = Waitlist.query.filter_by(event_id=event_id).order_by(Waitlist.position.desc()).first()
        next_position = (last_position.position + 1) if last_position else 1
        
        waitlist_entry = Waitlist(
            event_id=event_id,
            user_id=current_user.id,
            position=next_position,
            status='active'
        )
        db.session.add(waitlist_entry)
        
        # Create notification
        notification = Notification(
            user_id=current_user.id,
            message=f'You have been added to the waitlist for "{event.name}". Position: {next_position}',
            type=NotificationType.WAITLIST,
            data={'event_id': event.id, 'position': next_position}
        )
        db.session.add(notification)
        
        db.session.commit()
        
        # Log action
        AuditLog.log_action(
            user_id=current_user.id,
            action='join_waitlist',
            entity='waitlist',
            entity_id=waitlist_entry.id,
            details=f"User {current_user.username} joined waitlist for event {event.name}",
            request=request
        )
        
        flash(f'Event is full! You have been added to the waitlist at position {next_position}.', 'info')
    else:
        # Create registration
        registration = Registration(
            user_id=current_user.id,
            event_id=event_id,
            status='confirmed'
        )
        db.session.add(registration)
        db.session.commit()
        
        # Generate ticket
        ticket = Ticket(registration)
        db.session.add(ticket)
        db.session.commit()
        
        # Create notifications
        notification1 = Notification(
            user_id=current_user.id,
            message=f'You have successfully registered for "{event.name}"!',
            type=NotificationType.REGISTRATION,
            data={'event_id': event.id, 'registration_id': registration.id}
        )
        notification2 = Notification(
            user_id=current_user.id,
            message=f'Your ticket for "{event.name}" has been generated.',
            type=NotificationType.TICKET,
            data={'ticket_id': ticket.id, 'registration_id': registration.id}
        )
        db.session.add(notification1)
        db.session.add(notification2)
        db.session.commit()
        
        # Log action
        AuditLog.log_action(
            user_id=current_user.id,
            action='register',
            entity='registration',
            entity_id=registration.id,
            details=f"User {current_user.username} registered for event {event.name}",
            request=request
        )
        
        flash('Registration successful! Your ticket has been generated.', 'success')
    
    return redirect(url_for('events.detail', event_id=event.id))


@events_bp.route('/<int:event_id>/cancel_registration', methods=['POST'])
@login_required
def cancel_registration(event_id):
    """Cancel registration for an event."""
    event = Event.query.get_or_404(event_id)
    
    registration = Registration.query.filter(
        Registration.event_id == event_id,
        Registration.user_id == current_user.id
    ).first()
    
    if not registration:
        flash('You are not registered for this event.', 'error')
        return redirect(url_for('events.detail', event_id=event.id))
    
    # Cancel registration
    registration.cancel()
    
    # Create notification
    notification = Notification(
        user_id=current_user.id,
        message=f'Your registration for "{event.name}" has been cancelled.',
        type=NotificationType.REGISTRATION_CANCELLED,
        data={'event_id': event.id, 'registration_id': registration.id}
    )
    db.session.add(notification)
    
    # Promote next waitlisted user if available
    waitlist_entry = Waitlist.query.filter(
        Waitlist.event_id == event_id,
        Waitlist.status == 'active'
    ).order_by(Waitlist.position).first()
    
    if waitlist_entry:
        # Create new registration for waitlisted user
        new_registration = Registration(
            user_id=waitlist_entry.user_id,
            event_id=event_id,
            status='confirmed'
        )
        db.session.add(new_registration)
        db.session.commit()
        
        # Generate ticket
        new_ticket = Ticket(new_registration)
        db.session.add(new_ticket)
        db.session.commit()
        
        # Promote waitlist entry
        waitlist_entry.promote()
        
        # Notify promoted user
        promoted_notification = Notification(
            user_id=waitlist_entry.user_id,
            message=f'You have been promoted from the waitlist for "{event.name}"! Your registration is now confirmed.',
            type=NotificationType.WAITLIST_PROMOTION,
            data={'event_id': event.id, 'registration_id': new_registration.id}
        )
        db.session.add(promoted_notification)
        
        # Reposition remaining waitlist entries
        remaining_entries = Waitlist.query.filter(
            Waitlist.event_id == event_id,
            Waitlist.status == 'active',
            Waitlist.position > waitlist_entry.position
        ).order_by(Waitlist.position).all()
        
        for entry in remaining_entries:
            entry.position -= 1
        db.session.commit()
    
    # Log action
    AuditLog.log_action(
        user_id=current_user.id,
        action='cancel_registration',
        entity='registration',
        entity_id=registration.id,
        details=f"User {current_user.username} cancelled registration for event {event.name}",
        request=request
    )
    
    flash('Your registration has been cancelled.', 'success')
    return redirect(url_for('events.detail', event_id=event.id))
