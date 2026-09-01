"""
EventSphere - Background Tasks Scheduler
"""

from flask_apscheduler import APScheduler
import os
import logging
from datetime import datetime
from app.models.event import Event, EventStatus
from app.models.budget import Budget
from app.models.budget import Budget
from app.models.approval import ApprovalRequest, ApprovalStatus
from app.models.registration import Registration, RegistrationStatus
from app.models.event_vendor import EventVendor, EventVendorStatus
from app.models.notification import Notification, NotificationType
from app import db

# Initialize scheduler
scheduler = APScheduler()

# Setup basic logging for scheduler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("eventsphere_scheduler")

def close_past_registrations():
    """Scheduled task to close registration for past events."""
    logger.info("Running task: close_past_registrations")
    from app import create_app
    app = create_app()
    with app.app_context():
        try:
            today = datetime.now().date()
            # Find all open events where date is in the past
            past_events = Event.query.filter(
                Event.date < today,
                Event.status == EventStatus.REGISTRATION_OPEN
            ).all()
            
            count = 0
            for event in past_events:
                event.status = EventStatus.COMPLETED
                count += 1
                
            if count > 0:
                db.session.commit()
                logger.info(f"Closed registration for {count} past events.")
            else:
                logger.info("No past events to close.")
        except Exception as e:
            logger.error(f"Error in close_past_registrations: {e}")
            db.session.rollback()

def auto_reject_stale_approvals():
    """Auto reject approval requests older than 30 days."""
    logger.info("Running task: auto_reject_stale_approvals")
    from app import create_app
    app = create_app()
    with app.app_context():
        try:
            from datetime import timedelta
            threshold = datetime.utcnow() - timedelta(days=30)
            stale_requests = ApprovalRequest.query.filter(
                ApprovalRequest.status == ApprovalStatus.PENDING,
                ApprovalRequest.requested_at < threshold
            ).all()
            
            count = 0
            for req in stale_requests:
                req.status = ApprovalStatus.REJECTED
                req.expense.status = 'rejected'
                req.notes = "System Auto-Reject: Request stale for > 30 days."
                count += 1
                
            if count > 0:
                db.session.commit()
                logger.info(f"Auto-rejected {count} stale approval requests.")
            else:
                logger.info("No stale approval requests found.")
        except Exception as e:
            logger.error(f"Error in auto_reject_stale_approvals: {e}")
            db.session.rollback()

def send_event_reminders():
    """Notify confirmed registrants ~24h before their event."""
    logger.info("Running task: send_event_reminders")
    from app import create_app
    app = create_app()
    with app.app_context():
        try:
            from datetime import timedelta
            now = datetime.now()
            tomorrow = now.date() + timedelta(days=1)
            
            # Find events happening tomorrow
            events_tomorrow = Event.query.filter_by(date=tomorrow).all()
            count = 0
            
            for event in events_tomorrow:
                # Find confirmed registrations without a reminder sent
                regs = Registration.query.filter_by(
                    event_id=event.id, 
                    status=RegistrationStatus.CONFIRMED,
                    reminder_sent=False
                ).all()
                
                for reg in regs:
                    notif = Notification(
                        user_id=reg.user_id,
                        message=f'Reminder: The event "{event.name}" is happening tomorrow!',
                        type=NotificationType.SYSTEM,
                        data={'event_id': event.id, 'origin': 'system'}
                    )
                    db.session.add(notif)
                    reg.reminder_sent = True
                    count += 1
                    
            if count > 0:
                db.session.commit()
                logger.info(f"Sent {count} event reminders.")
            else:
                logger.info("No event reminders to send.")
        except Exception as e:
            logger.error(f"Error in send_event_reminders: {e}")
            db.session.rollback()

def send_vendor_reminders():
    """Notify assigned vendors ~24h before their event."""
    logger.info("Running task: send_vendor_reminders")
    from app import create_app
    app = create_app()
    with app.app_context():
        try:
            from datetime import timedelta
            now = datetime.now()
            tomorrow = now.date() + timedelta(days=1)
            
            events_tomorrow = Event.query.filter_by(date=tomorrow).all()
            count = 0
            
            for event in events_tomorrow:
                # Find confirmed vendor assignments without a reminder sent
                assignments = EventVendor.query.filter_by(
                    event_id=event.id,
                    status=EventVendorStatus.CONFIRMED,
                    reminder_sent=False
                ).all()
                
                for assign in assignments:
                    notif = Notification(
                        user_id=assign.vendor.user_id,
                        message=f'Reminder: You are scheduled to provide {assign.service} for "{event.name}" tomorrow!',
                        type=NotificationType.SYSTEM,
                        data={'event_id': event.id, 'origin': 'system'}
                    )
                    db.session.add(notif)
                    assign.reminder_sent = True
                    count += 1
                    
            if count > 0:
                db.session.commit()
                logger.info(f"Sent {count} vendor reminders.")
            else:
                logger.info("No vendor reminders to send.")
        except Exception as e:
            logger.error(f"Error in send_vendor_reminders: {e}")
            db.session.rollback()

def init_scheduler(app):
    """
    Initialize APScheduler with Flask.
    Includes dev-server double-init guard to prevent jobs from running twice
    when Werkzeug's reloader spawns a second process.
    """
    if app.config.get('TESTING') or app.config.get('DISABLE_SCHEDULER'):
        return

    # In dev mode, Werkzeug runs a master process and a worker process.
    # We only want to start the scheduler in the worker process.
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        scheduler.init_app(app)
        
        # Add Jobs (Note: In production, consider using a separate worker process / celery)
        
        # Run every day at midnight
        scheduler.add_job(id='close_past_registrations', func=close_past_registrations, trigger='cron', hour=0, minute=0)
        
        # Run every day at 1 AM
        scheduler.add_job(id='auto_reject_stale_approvals', func=auto_reject_stale_approvals, trigger='cron', hour=1, minute=0)
        
        # Run every day at 8 AM (Reminders)
        scheduler.add_job(id='send_event_reminders', func=send_event_reminders, trigger='cron', hour=8, minute=0)
        scheduler.add_job(id='send_vendor_reminders', func=send_vendor_reminders, trigger='cron', hour=8, minute=30)
        
        try:
            scheduler.start()
            app.logger.info("APScheduler started successfully.")
        except Exception as e:
            app.logger.error(f"Failed to start APScheduler: {e}")
