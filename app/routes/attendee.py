"""
EventSphere - Attendee Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, abort
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.event import Event, EventStatus
from app.models.registration import Registration
from app.models.ticket import Ticket
from app.models.waitlist import Waitlist
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.models.feedback import Feedback
from app.models.notification import Notification
from app.models.user import UserRole
import os

attendee_bp = Blueprint('attendee', __name__, template_folder='../templates/attendee', url_prefix='/attendee')


@attendee_bp.before_request
@login_required
def check_attendee():
    """Ensure only attendee can access attendee routes."""
    if current_user.role != UserRole.ATTENDEE:
        abort(403)


@attendee_bp.route('/')
@attendee_bp.route('/dashboard')
def dashboard():
    """Attendee dashboard."""
    # My registrations
    registrations = Registration.query.filter_by(user_id=current_user.id).order_by(Registration.registration_date.desc()).all()
    
    # Upcoming events
    upcoming_events = Event.query.join(Registration).filter(
        Registration.user_id == current_user.id,
        Event.date >= datetime.utcnow().date(),
        Event.status.in_([EventStatus.PUBLISHED, EventStatus.REGISTRATION_OPEN])
    ).order_by(Event.date).all()
    
    # Past events
    past_events = Event.query.join(Registration).filter(
        Registration.user_id == current_user.id,
        Event.date < datetime.utcnow().date()
    ).order_by(Event.date.desc()).all()
    
    # Waitlist entries
    waitlist_entries = Waitlist.query.filter(
        Waitlist.user_id == current_user.id,
        Waitlist.status == 'active'
    ).order_by(Waitlist.position).all()
    
    # Unread notifications count
    unread_count = Notification.query.filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    # Certificates
    certificates = Certificate.query.join(Registration).filter(
        Registration.user_id == current_user.id
    ).order_by(Certificate.issued_at.desc()).all()
    
    return render_template('dashboard.html',
                          registrations=registrations,
                          upcoming_events=upcoming_events,
                          past_events=past_events,
                          waitlist_entries=waitlist_entries,
                          unread_count=unread_count,
                          certificates=certificates,
                          title='My Dashboard')


@attendee_bp.route('/events')
def events():
    """Browse all events."""
    from datetime import date
    
    # Get all published/registration_open events
    events = Event.query.filter(
        Event.status.in_([EventStatus.PUBLISHED, EventStatus.REGISTRATION_OPEN]),
        Event.date >= date.today()
    ).order_by(Event.date, Event.start_time).all()
    
    # Get user's registrations
    registered_event_ids = [r.event_id for r in Registration.query.filter_by(user_id=current_user.id).all()]
    waitlisted_event_ids = [w.event_id for w in Waitlist.query.filter(
        Waitlist.user_id == current_user.id,
        Waitlist.status == 'active'
    ).all()]
    
    return render_template('events/index.html',
                          events=events,
                          registered_event_ids=registered_event_ids,
                          waitlisted_event_ids=waitlisted_event_ids,
                          title='All Events')


@attendee_bp.route('/events/<int:event_id>')
def event_detail(event_id):
    """View event details."""
    event = Event.query.get_or_404(event_id)
    
    # Check registration status
    registration = Registration.query.filter(
        Registration.event_id == event_id,
        Registration.user_id == current_user.id
    ).first()
    
    waitlist_entry = Waitlist.query.filter(
        Waitlist.event_id == event_id,
        Waitlist.user_id == current_user.id,
        Waitlist.status == 'active'
    ).first()
    
    return render_template('events/detail.html',
                          event=event,
                          registration=registration,
                          waitlist_entry=waitlist_entry,
                          title=event.name)


@attendee_bp.route('/registrations')
def my_registrations():
    """View my registrations."""
    registrations = Registration.query.filter_by(user_id=current_user.id).order_by(Registration.registration_date.desc()).all()
    
    return render_template('registrations/index.html',
                          registrations=registrations,
                          title='My Registrations')


@attendee_bp.route('/tickets')
def my_tickets():
    """View my tickets."""
    tickets = Ticket.query.join(Registration).filter(
        Registration.user_id == current_user.id
    ).order_by(Ticket.created_at.desc()).all()
    
    return render_template('tickets/index.html',
                          tickets=tickets,
                          title='My Tickets')


@attendee_bp.route('/tickets/<int:ticket_id>')
def view_ticket(ticket_id):
    """View a ticket with QR code."""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Verify this ticket belongs to current user
    if ticket.registration.user_id != current_user.id:
        abort(403)
    
    # Generate QR code if not already generated
    if not ticket.qr_code_path:
        upload_path = current_user._get_current_object().app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
        qr_path = os.path.join(upload_path, 'qr_codes', f'qr_{ticket.id}.png')
        ticket.generate_qr_code(qr_path)
    
    return render_template('tickets/view.html',
                          ticket=ticket,
                          title=f'Ticket {ticket.ticket_id}')


@attendee_bp.route('/tickets/<int:ticket_id>/download')
def download_ticket(ticket_id):
    """Download ticket as PDF."""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Verify this ticket belongs to current user
    if ticket.registration.user_id != current_user.id:
        abort(403)
    
    # Generate PDF ticket
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import io
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, alignment=TA_CENTER)
    
    # Story
    story = []
    story.append(Paragraph("EVENT TICKET", ParagraphStyle('Title', fontSize=24, alignment=TA_CENTER)))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(ticket.event_name, title_style))
    story.append(Spacer(1, 0.2 * inch))
    
    # Ticket details table
    data = [
        ['Attendee:', ticket.attendee_name],
        ['Event:', ticket.event_name],
        ['Date:', ticket.event_date.strftime('%B %d, %Y')],
        ['Time:', ticket.event_time],
        ['Venue:', ticket.venue_name],
        ['Ticket ID:', ticket.ticket_id]
    ]
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3 * inch))
    
    # QR Code
    qr_path = ticket.qr_code_path
    if qr_path and os.path.exists(os.path.join('app/static', qr_path)):
        story.append(Paragraph("QR Code:", ParagraphStyle('Normal', fontSize=12, spaceAfter=10)))
        story.append(Image(os.path.join('app/static', qr_path), width=2*inch, height=2*inch))
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'ticket_{ticket.ticket_id}.pdf',
        mimetype='application/pdf'
    )


@attendee_bp.route('/notifications')
def notifications():
    """View my notifications."""
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # Mark all as read
    unread = Notification.query.filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).all()
    for n in unread:
        n.mark_as_read()
    
    return render_template('notifications/index.html',
                          notifications=notifications,
                          title='My Notifications')


@attendee_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        abort(403)
    
    notification.mark_as_read()
    return redirect(url_for('attendee.notifications'))


@attendee_bp.route('/certificates')
def my_certificates():
    """View my certificates."""
    certificates = Certificate.query.join(Registration).filter(
        Registration.user_id == current_user.id
    ).order_by(Certificate.issued_at.desc()).all()
    
    return render_template('certificates/index.html',
                          certificates=certificates,
                          title='My Certificates')


@attendee_bp.route('/certificates/<int:certificate_id>/download')
def download_certificate(certificate_id):
    """Download a certificate."""
    certificate = Certificate.query.get_or_404(certificate_id)
    
    # Verify this certificate belongs to current user
    if certificate.registration.user_id != current_user.id:
        abort(403)
    
    # Generate PDF if not already generated
    if not certificate.file_path:
        upload_path = current_user._get_current_object().app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
        cert_path = os.path.join(upload_path, 'certificates', f'certificate_{certificate.id}.pdf')
        certificate.generate_pdf(cert_path)
    
    # Return the file
    file_path = os.path.join('app/static', certificate.file_path)
    return send_file(
        file_path,
        as_attachment=True,
        download_name=f'certificate_{certificate.certificate_id}.pdf',
        mimetype='application/pdf'
    )


@attendee_bp.route('/events/<int:event_id>/feedback', methods=['GET', 'POST'])
def submit_feedback(event_id):
    """Submit feedback for an event."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user attended this event
    registration = Registration.query.filter(
        Registration.event_id == event_id,
        Registration.user_id == current_user.id
    ).first()
    
    if not registration:
        flash('You are not registered for this event.', 'error')
        return redirect(url_for('attendee.dashboard'))
    
    # Check if event is completed
    if event.status != EventStatus.COMPLETED:
        flash('Feedback can only be submitted after the event is completed.', 'error')
        return redirect(url_for('attendee.dashboard'))
    
    # Check if already submitted feedback
    existing_feedback = Feedback.query.filter_by(registration_id=registration.id).first()
    if existing_feedback:
        flash('You have already submitted feedback for this event.', 'error')
        return redirect(url_for('attendee.dashboard'))
    
    from app.forms.feedback_forms import FeedbackForm
    form = FeedbackForm()
    
    if form.validate_on_submit():
        feedback = Feedback(
            registration_id=registration.id,
            user_id=current_user.id,
            event_id=event_id,
            rating=form.rating.data,
            comments=form.comments.data.strip() if form.comments.data else None,
            suggestions=form.suggestions.data.strip() if form.suggestions.data else None
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('attendee.dashboard'))
    
    return render_template('feedback/submit.html',
                          event=event,
                          form=form,
                          title=f'Feedback for {event.name}')
