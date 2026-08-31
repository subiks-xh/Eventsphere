"""
EventSphere - Venue Routes
CRUD operations for venues
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.venue import Venue
from app.models.user import UserRole
from app.models.event import Event
from app.forms.venue_forms import VenueForm
from app.models.audit_log import AuditLog

# Create blueprint
venue_bp = Blueprint('venue', __name__, template_folder='../templates/venue', url_prefix='/venues')


@venue_bp.before_request
@login_required
def check_admin_or_organizer():
    """Ensure only admin or organizer can access venue routes."""
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        abort(403)


@venue_bp.route('/')
def index():
    """List all venues."""
    venues = Venue.query.order_by(Venue.name).all()
    
    # Log view action
    AuditLog.log_action(
        user_id=current_user.id,
        action='view',
        entity='venue_list',
        details=f"User {current_user.username} viewed venue list",
        request=request
    )
    
    return render_template('index.html', venues=venues, title='All Venues')


@venue_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new venue."""
    form = VenueForm()
    
    if form.validate_on_submit():
        # Check if venue with same name already exists
        existing = Venue.query.filter_by(name=form.name.data.strip()).first()
        if existing:
            form.name.errors.append('A venue with this name already exists.')
            return render_template('create.html', form=form, title='Create Venue')
        
        venue = Venue(
            name=form.name.data.strip(),
            address=form.address.data.strip(),
            city=form.city.data.strip(),
            state=form.state.data.strip() if form.state.data else None,
            postal_code=form.postal_code.data.strip() if form.postal_code.data else None,
            country=form.country.data.strip(),
            capacity=form.capacity.data or 0,
            description=form.description.data.strip() if form.description.data else None,
            contact_phone=form.contact_phone.data.strip() if form.contact_phone.data else None,
            contact_email=form.contact_email.data.strip() if form.contact_email.data else None,
            status=form.status.data or 'active'
        )
        
        db.session.add(venue)
        db.session.commit()
        
        # Log creation action
        AuditLog.log_action(
            user_id=current_user.id,
            action='create',
            entity='venue',
            entity_id=venue.id,
            details=f"User {current_user.username} created venue {venue.name}",
            request=request
        )
        
        flash('Venue created successfully!', 'success')
        return redirect(url_for('venue.detail', venue_id=venue.id))
    
    return render_template('create.html', form=form, title='Create Venue')


@venue_bp.route('/<int:venue_id>')
def detail(venue_id):
    """View venue details and its events."""
    venue = Venue.query.get_or_404(venue_id)
    events = venue.get_events()
    
    # Log view action
    AuditLog.log_action(
        user_id=current_user.id,
        action='view',
        entity='venue',
        entity_id=venue.id,
        details=f"User {current_user.username} viewed venue {venue.name}",
        request=request
    )
    
    return render_template('detail.html', venue=venue, events=events, title=venue.name)


@venue_bp.route('/<int:venue_id>/edit', methods=['GET', 'POST'])
def edit(venue_id):
    """Edit a venue."""
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(obj=venue)
    
    if form.validate_on_submit():
        # Check if another venue has the same name
        existing = Venue.query.filter(
            Venue.name.ilike(form.name.data.strip()),
            Venue.id != venue_id
        ).first()
        if existing:
            form.name.errors.append('A venue with this name already exists.')
            return render_template('edit.html', form=form, venue=venue, title=f'Edit {venue.name}')
        
        # Update venue
        venue.name = form.name.data.strip()
        venue.address = form.address.data.strip()
        venue.city = form.city.data.strip()
        venue.state = form.state.data.strip() if form.state.data else None
        venue.postal_code = form.postal_code.data.strip() if form.postal_code.data else None
        venue.country = form.country.data.strip()
        venue.capacity = form.capacity.data or 0
        venue.description = form.description.data.strip() if form.description.data else None
        venue.contact_phone = form.contact_phone.data.strip() if form.contact_phone.data else None
        venue.contact_email = form.contact_email.data.strip() if form.contact_email.data else None
        venue.status = form.status.data or 'active'
        
        db.session.commit()
        
        # Log update action
        AuditLog.log_action(
            user_id=current_user.id,
            action='update',
            entity='venue',
            entity_id=venue.id,
            details=f"User {current_user.username} updated venue {venue.name}",
            request=request
        )
        
        flash('Venue updated successfully!', 'success')
        return redirect(url_for('venue.detail', venue_id=venue.id))
    
    return render_template('edit.html', form=form, venue=venue, title=f'Edit {venue.name}')


@venue_bp.route('/<int:venue_id>/delete', methods=['POST'])
def delete(venue_id):
    """Delete a venue."""
    venue = Venue.query.get_or_404(venue_id)
    
    # Check if venue has events
    if venue.event_count > 0:
        flash('Cannot delete venue with assigned events. Please reassign or delete events first.', 'error')
        return redirect(url_for('venue.detail', venue_id=venue.id))
    
    db.session.delete(venue)
    db.session.commit()
    
    # Log deletion action
    AuditLog.log_action(
        user_id=current_user.id,
        action='delete',
        entity='venue',
        entity_id=venue_id,
        details=f"User {current_user.username} deleted venue {venue.name}",
        request=request
    )
    
    flash('Venue deleted successfully!', 'success')
    return redirect(url_for('venue.index'))
