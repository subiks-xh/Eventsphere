"""
EventSphere - Vendor Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.vendor import Vendor
from app.models.event import Event
from app.models.event_vendor import EventVendor, EventVendorStatus
from app.models.user import UserRole
from app.models.audit_log import AuditLog

vendor_bp = Blueprint('vendor', __name__, template_folder='../templates/vendor', url_prefix='/vendor')


@vendor_bp.before_request
@login_required
def check_vendor():
    """Ensure only vendor can access vendor routes."""
    if current_user.role != UserRole.VENDOR:
        abort(403)


@vendor_bp.route('/')
@vendor_bp.route('/dashboard')
def dashboard():
    """Vendor dashboard."""
    # Get vendor profile
    vendor = Vendor.query.filter_by(user_id=current_user.id).first()
    
    if not vendor:
        flash('Please complete your vendor profile.', 'warning')
        return redirect(url_for('vendor.profile'))
    
    # Get assigned events
    assigned_events = vendor.assigned_events
    
    # Get pending assignments
    pending_assignments = EventVendor.query.filter(
        EventVendor.vendor_id == vendor.id,
        EventVendor.status == EventVendorStatus.PENDING
    ).all()
    
    # Get confirmed assignments
    confirmed_assignments = EventVendor.query.filter(
        EventVendor.vendor_id == vendor.id,
        EventVendor.status == EventVendorStatus.CONFIRMED
    ).all()
    
    # Get completed assignments
    completed_assignments = EventVendor.query.filter(
        EventVendor.vendor_id == vendor.id,
        EventVendor.status == EventVendorStatus.COMPLETED
    ).all()
    
    return render_template('dashboard.html',
                          vendor=vendor,
                          assigned_events=assigned_events,
                          pending_assignments=pending_assignments,
                          confirmed_assignments=confirmed_assignments,
                          completed_assignments=completed_assignments,
                          title='Vendor Dashboard')


@vendor_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """Manage vendor profile."""
    vendor = Vendor.query.filter_by(user_id=current_user.id).first()
    
    from app.forms.vendor_forms import VendorForm
    form = VendorForm(obj=vendor) if vendor else VendorForm()
    
    if form.validate_on_submit():
        if not vendor:
            vendor = Vendor(
                user_id=current_user.id,
                business_name=form.business_name.data.strip(),
                contact_person=form.contact_person.data.strip(),
                email=form.email.data.strip(),
                phone=form.phone.data.strip(),
                service=form.service.data,
                description=form.description.data.strip() if form.description.data else None,
                address=form.address.data.strip() if form.address.data else None,
                status=form.status.data
            )
            db.session.add(vendor)
        else:
            vendor.business_name = form.business_name.data.strip()
            vendor.contact_person = form.contact_person.data.strip()
            vendor.email = form.email.data.strip()
            vendor.phone = form.phone.data.strip()
            vendor.service = form.service.data
            vendor.description = form.description.data.strip() if form.description.data else None
            vendor.address = form.address.data.strip() if form.address.data else None
            vendor.status = form.status.data
        
        db.session.commit()
        
        # Log action
        AuditLog.log_action(
            user_id=current_user.id,
            action='update_profile',
            entity='vendor',
            entity_id=vendor.id,
            details=f"User {current_user.username} updated vendor profile",
            request=request
        )
        
        flash('Vendor profile updated successfully!', 'success')
        return redirect(url_for('vendor.dashboard'))
    
    return render_template('profile.html', form=form, vendor=vendor, title='Vendor Profile')


@vendor_bp.route('/events')
def events():
    """View assigned events."""
    vendor = Vendor.query.filter_by(user_id=current_user.id).first()
    
    if not vendor:
        flash('Please complete your vendor profile first.', 'warning')
        return redirect(url_for('vendor.profile'))
    
    assignments = EventVendor.query.filter_by(vendor_id=vendor.id).order_by(EventVendor.assigned_at.desc()).all()
    
    return render_template('events/index.html',
                          assignments=assignments,
                          title='My Assigned Events')


@vendor_bp.route('/events/<int:assignment_id>/update', methods=['POST'])
def update_status(assignment_id):
    """Update service status for an assignment."""
    assignment = EventVendor.query.get_or_404(assignment_id)
    
    # Verify this assignment belongs to current vendor
    vendor = Vendor.query.filter_by(user_id=current_user.id).first()
    if not vendor or assignment.vendor_id != vendor.id:
        abort(403)
    
    new_status = request.form.get('status')
    
    if new_status not in ['pending', 'confirmed', 'cancelled', 'completed']:
        flash('Invalid status.', 'error')
        return redirect(url_for('vendor.events'))
    
    assignment.status = new_status
    db.session.commit()
    
    # Log action
    AuditLog.log_action(
        user_id=current_user.id,
        action='update_status',
        entity='event_vendor',
        entity_id=assignment.id,
        details=f"User {current_user.username} updated status to {new_status}",
        request=request
    )
    
    flash('Service status updated successfully!', 'success')
    return redirect(url_for('vendor.events'))
