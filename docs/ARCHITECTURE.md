# EventSphere - Architecture Documentation

## Overview
EventSphere is a monolithic, server-rendered web application built using Flask. It uses a scalable **Application Factory** pattern combined with **Blueprints** to organize the code logically into domain-specific modules.

## Technology Stack
- **Framework:** Flask 2.3.3
- **Database ORM:** SQLAlchemy 2.0 (via Flask-SQLAlchemy 3.1)
- **Database Migration:** Alembic (via Flask-Migrate)
- **Authentication:** Flask-Login & Werkzeug password hashing
- **Frontend:** Jinja2 templating, Bootstrap 5.3, Chart.js for data visualization
- **Background Jobs:** APScheduler (via Flask-APScheduler)
- **Database:** SQLite (development) / PostgreSQL (production)

## Project Structure
```
EventSphere/
├── app/                      # Application core
│   ├── __init__.py           # App Factory initialization
│   ├── models/               # SQLAlchemy Database Models
│   ├── routes/               # Flask Blueprints (Controllers)
│   ├── templates/            # Jinja2 Views
│   ├── static/               # CSS, JS, Images, Uploads
│   ├── forms/                # WTForms definitions
│   ├── utils/                # Helper utilities (QR, Analytics, Forecasting, Optimization)
│   └── scheduler.py          # APScheduler background tasks
├── tests/                    # Pytest test suite
├── scripts/                  # Shell/PowerShell helper scripts
├── docs/                     # Markdown documentation
├── migrations/               # Alembic DB migration files
├── config.py                 # Environment-specific configuration
├── run.py                    # Application entrypoint
└── requirements.txt          # Python dependencies
```

## Key Patterns
- **Blueprints:** Routing is split into domain-specific modules (`auth`, `admin`, `organizer`, `attendee`, `vendor`, `venue`, `events`, `budget`, `api`).
- **Service Utilities:** Heavy logic like `analytics`, `forecasting`, and `optimization` are abstracted into `app/utils/` to keep controllers thin.
- **REST API (`/api/v1`):** Serves authenticated endpoints designed for dynamic frontend components, secured via `Flask-Login`.
- **RBAC (Role-Based Access Control):** Uses `UserRole` (Admin, Organizer, Attendee, Vendor) verified actively across routes.
