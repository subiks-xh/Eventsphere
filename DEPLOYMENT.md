# EventSphere Deployment Guide

## Production Checklist

Before deploying EventSphere to a production environment, ensure the following configurations are set:

1. **Database:** Use PostgreSQL instead of SQLite for production. Update `SQLALCHEMY_DATABASE_URI`.
2. **Secret Key:** Ensure `SECRET_KEY` is a strong, random string and stored securely (e.g., in `.env`).
3. **Debug Mode:** `FLASK_DEBUG` must be `False`.
4. **Static Files:** Use a production web server (like Nginx) to serve static files.

## Running Background Tasks (APScheduler)

EventSphere uses `Flask-APScheduler` for background tasks, such as auto-rejecting stale approvals and closing past registrations.

### ⚠️ Production Caveat

If you run EventSphere using a multi-worker WSGI server (like **Gunicorn** or **uWSGI**), the APScheduler initialized within the Flask app factory will start a separate scheduler instance inside *every* worker process. This leads to background jobs running multiple times simultaneously, which can cause data corruption and duplicate actions.

To prevent this:

1. **Disable In-App Scheduler:** Set `DISABLE_SCHEDULER=True` in your production environment variables.
2. **Run as a Separate Worker:** Run the scheduler as a standalone process (e.g., via a separate script or a dedicated container) that initializes the Flask app context and starts the APScheduler, ensuring only exactly one instance of the scheduler is running.
3. **Alternatively (Cron):** If you disable the in-app scheduler, you can expose the tasks as Flask CLI commands and trigger them using standard system cron jobs.

### Development Mode

In development mode (using `flask run` or `python run.py`), a double-init guard is included in `app/scheduler.py` that checks for `WERKZEUG_RUN_MAIN`. This ensures the scheduler only boots once in the worker process, avoiding the double-execution bug caused by Werkzeug's auto-reloader.
