"""
EventSphere - Application Entry Point
Run this file to start the application
"""

from app import create_app
import os
from config import config

config_name = os.environ.get('FLASK_ENV') or 'default'
app = create_app(config[config_name])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', True))
