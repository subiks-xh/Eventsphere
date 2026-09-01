"""
EventSphere - Error Routes
"""

from flask import Blueprint, render_template
from app import db

errors_bp = Blueprint('errors', __name__)


@errors_bp.app_errorhandler(403)
def forbidden_error(error):
    """403 Forbidden error handler."""
    return render_template('errors/403.html', error=error), 403


@errors_bp.app_errorhandler(404)
def not_found_error(error):
    """404 Not Found error handler."""
    return render_template('errors/404.html', error=error), 404


@errors_bp.app_errorhandler(500)
def internal_error(error):
    """500 Internal Server Error handler."""
    db.session.rollback()
    return render_template('errors/500.html', error=error), 500


@errors_bp.app_errorhandler(400)
def bad_request_error(error):
    """400 Bad Request error handler."""
    return render_template('errors/400.html', error=error), 400
