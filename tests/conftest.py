import pytest
import os
from app import create_app, db
from app.models.user import User, UserRole

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    os.environ['FLASK_ENV'] = 'testing'
    
    from config import config
    app = create_app(config['testing'])
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SERVER_NAME": "localhost"
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    """Initialize the database with a standard admin user."""
    with app.app_context():
        admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role=UserRole.ADMIN,
            password='adminpass'
        )
        db.session.add(admin)
        db.session.commit()
        return admin
