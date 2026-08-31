"""
EventSphere - Audit Log Model
"""

from datetime import datetime
from app import db


class AuditLog(db.Model):
    """Audit log model for tracking important actions."""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    entity = db.Column(db.String(100), nullable=False)
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def log_action(cls, user_id, action, entity, entity_id=None, details=None, request=None):
        """
        Log an action to the audit log.
        
        Args:
            user_id: User ID who performed the action
            action: Action performed (e.g., 'create', 'update', 'delete')
            entity: Entity type (e.g., 'event', 'user', 'registration')
            entity_id: ID of the entity
            details: Additional details
            request: Flask request object for IP and user agent
        """
        ip_address = None
        user_agent = None

        if request:
            ip_address = request.remote_addr
            user_agent = request.user_agent.string if hasattr(request, 'user_agent') else None

        log = cls(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log)
        db.session.commit()
        return log

    def __repr__(self):
        return f"<AuditLog {self.id} - {self.action} {self.entity}>"
