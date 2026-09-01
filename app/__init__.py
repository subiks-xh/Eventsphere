"""
EventSphere - Flask Application Factory
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

# Import models (to register with SQLAlchemy)
from app.models.user import User
from app.models.venue import Venue
from app.models.event import Event

# Other models will be imported when needed


def create_app(config_class=Config):
    """
    Application factory function.
    Creates and configures the Flask application.
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Initialize APScheduler
    from app.scheduler import init_scheduler
    init_scheduler(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.organizer import organizer_bp
    from app.routes.attendee import attendee_bp
    from app.routes.vendor import vendor_bp
    from app.routes.venue import venue_bp
    from app.routes.events import events_bp
    from app.routes.api import api_v1_bp
    from app.routes.errors import errors_bp
    from app.routes.budget import budget_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(organizer_bp, url_prefix='/organizer')
    app.register_blueprint(attendee_bp, url_prefix='/attendee')
    app.register_blueprint(vendor_bp, url_prefix='/vendor')
    app.register_blueprint(venue_bp, url_prefix='/venues')
    app.register_blueprint(events_bp, url_prefix='/events')
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    app.register_blueprint(budget_bp)
    app.register_blueprint(errors_bp)
    
    # Create upload directories
    upload_path = app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
    os.makedirs(upload_path, exist_ok=True)
    for subdir in ['tickets', 'certificates', 'qr_codes']:
        os.makedirs(os.path.join(upload_path, subdir), exist_ok=True)
    
    return app
