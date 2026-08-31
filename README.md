# EventSphere - Event Management System

A complete, polished, and functional event management system built with Flask, SQLAlchemy, and Bootstrap 5. Perfect for college project demonstrations.

## 🎯 Features

### Core Event Lifecycle
- ✅ **Event Management**: Create, edit, publish, cancel events
- ✅ **Venue Management**: Add venues, edit, delete, view details
- ✅ **Venue Conflict Detection**: Prevents double-booking venues at overlapping times
- ✅ **Registration System**: Attendees can register for events
- ✅ **Capacity Management**: Tracks confirmed registrations vs capacity
- ✅ **Waitlist System**: Automatic waitlist with position tracking
- ✅ **Automatic Waitlist Promotion**: When someone cancels, next waitlisted user is automatically promoted
- ✅ **Digital Tickets**: Generate tickets with unique IDs
- ✅ **QR Code Generation**: Each ticket has a QR code for check-in
- ✅ **Attendance Check-in**: Manual and QR-based check-in
- ✅ **Certificate Generation**: PDF certificates for eligible attendees
- ✅ **Vendor Management**: Add vendors, assign to events, manage services
- ✅ **Resource Management**: Track equipment, prevent over-allocation
- ✅ **Feedback System**: Post-event feedback collection
- ✅ **Notification System**: In-app notifications for all important actions

### User Roles & Dashboards
- ✅ **Admin Dashboard**: User management, statistics, audit logs
- ✅ **Organizer Dashboard**: Event management, registrations, analytics
- ✅ **Attendee Dashboard**: My events, tickets, certificates, notifications
- ✅ **Vendor Dashboard**: Assigned events, service status

### Analytics & Reports
- ✅ **Real-time Statistics**: KPIs based on actual database data
- ✅ **Charts**: Visualizations using Chart.js (to be implemented)
- ✅ **Event Reports**: Detailed reports with export options

### Security
- ✅ **Authentication**: Login, registration, logout
- ✅ **Role-Based Access Control**: Different permissions for each role
- ✅ **Password Hashing**: Secure password storage
- ✅ **CSRF Protection**: Form security
- ✅ **Session Management**: Secure user sessions

## 🏗️ Technology Stack

- **Backend**: Flask 3.0
- **Database**: SQLAlchemy 2.0 (SQLite for development, PostgreSQL compatible)
- **ORM**: Flask-SQLAlchemy
- **Migrations**: Flask-Migrate
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF, WTForms
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Icons**: Bootstrap Icons
- **Charts**: Chart.js
- **QR Codes**: qrcode, Pillow
- **PDF Generation**: ReportLab
- **Environment**: python-dotenv

## 📁 Project Structure

```
EventSphere/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration
│   │
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── venue.py             # Venue model
│   │   ├── event.py             # Event model
│   │   ├── registration.py      # Registration model
│   │   ├── ticket.py            # Ticket model
│   │   ├── waitlist.py          # Waitlist model
│   │   ├── vendor.py            # Vendor model
│   │   ├── resource.py          # Resource model
│   │   ├── event_vendor.py      # Event-Vendor association
│   │   ├── event_resource.py    # Event-Resource association
│   │   ├── attendance.py        # Attendance model
│   │   ├── certificate.py       # Certificate model
│   │   ├── feedback.py          # Feedback model
│   │   ├── notification.py      # Notification model
│   │   └── audit_log.py         # Audit log model
│   │
│   ├── forms/                   # WTForms form classes
│   │   ├── __init__.py
│   │   ├── auth_forms.py        # Login, registration forms
│   │   ├── user_forms.py        # User management forms
│   │   ├── venue_forms.py       # Venue forms
│   │   ├── event_forms.py       # Event forms
│   │   ├── registration_forms.py
│   │   ├── vendor_forms.py       # Vendor forms
│   │   └── feedback_forms.py    # Feedback forms
│   │
│   ├── routes/                  # Flask blueprints
│   │   ├── __init__.py
│   │   ├── main.py              # Main routes
│   │   ├── auth.py              # Authentication routes
│   │   ├── admin.py             # Admin routes
│   │   ├── organizer.py         # Organizer routes
│   │   ├── attendee.py          # Attendee routes
│   │   ├── vendor.py            # Vendor routes
│   │   ├── venue.py             # Venue routes
│   │   ├── events.py            # Event routes
│   │   ├── api.py               # API routes
│   │   └── errors.py            # Error handlers
│   │
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html            # Base template
│   │   ├── layout.html          # Layout with navbar
│   │   ├── auth/               # Authentication templates
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── admin/              # Admin templates
│   │   │   ├── dashboard.html
│   │   │   ├── users/
│   │   │   │   └── index.html
│   │   │   └── audit_logs.html
│   │   ├── organizer/          # Organizer templates
│   │   │   ├── dashboard.html
│   │   │   ├── events/
│   │   │   │   ├── index.html
│   │   │   │   ├── registrations.html
│   │   │   │   ├── checkin.html
│   │   │   │   └── certificates.html
│   │   │   └── statistics.html
│   │   ├── attendee/           # Attendee templates
│   │   │   ├── dashboard.html
│   │   │   ├── events/
│   │   │   │   └── index.html
│   │   │   ├── tickets/
│   │   │   │   ├── index.html
│   │   │   │   └── view.html
│   │   │   ├── notifications/
│   │   │   │   └── index.html
│   │   │   ├── certificates/
│   │   │   │   └── index.html
│   │   │   └── feedback/
│   │   │       └── submit.html
│   │   ├── vendor/             # Vendor templates
│   │   │   ├── dashboard.html
│   │   │   ├── profile.html
│   │   │   └── events/
│   │   │       └── index.html
│   │   ├── venue/              # Venue templates
│   │   │   ├── index.html
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   └── detail.html
│   │   ├── events/             # Event templates
│   │   │   ├── index.html
│   │   │   ├── detail.html
│   │   │   ├── create.html
│   │   │   └── edit.html
│   │   ├── main/               # Main templates
│   │   │   └── index.html
│   │   └── errors/             # Error templates
│   │       ├── 403.html
│   │       ├── 404.html
│   │       └── 500.html
│   │
│   ├── static/                  # Static files
│   │   ├── css/
│   │   │   └── style.css       # Custom styles
│   │   ├── js/
│   │   │   └── main.js          # Custom JavaScript
│   │   └── images/
│   │       └── logo.png
│   │
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── helpers.py
│
├── migrations/                # Flask-Migrate migrations
├── instance/                  # Instance folder (SQLite database)
├── tests/                     # Test files
├── config.py                  # Configuration
├── run.py                     # Application entry point
├── seed.py                    # Demo data seeder
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore rules
├── .flaskenv                  # Flask environment variables
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd EventSphere

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings (optional)
# The default settings work for development
```

### 3. Initialize Database

```bash
# Set Flask environment
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4. Seed Demo Data

```bash
# Run the seed script to populate demo data
python seed.py
```

### 5. Run the Application

```bash
# Start the development server
flask run
# or
python run.py
```

The application will be available at: **http://127.0.0.1:5000**

## 👤 Demo Accounts

After seeding the database, you can log in with these accounts:

| Role | Username | Password | Email |
|------|----------|----------|-------|
| Admin | `admin` | `admin123` | admin@eventsphere.com |
| Organizer | `organizer1` | `organizer123` | organizer1@eventsphere.com |
| Organizer | `organizer2` | `organizer123` | organizer2@eventsphere.com |
| Attendee | `attendee1` | `attendee123` | attendee1@eventsphere.com |
| Attendee | `attendee2` | `attendee123` | attendee2@eventsphere.com |
| Attendee | `attendee3` | `attendee123` | attendee3@eventsphere.com |
| Attendee | `attendee4` | `attendee123` | attendee4@eventsphere.com |
| Attendee | `attendee5` | `attendee123` | attendee5@eventsphere.com |
| Vendor | `vendor1` | `vendor123` | vendor1@catering.com |
| Vendor | `vendor2` | `vendor123` | vendor2@decoration.com |
| Vendor | `vendor3` | `vendor123` | vendor3@photography.com |

## 🧪 Testing Scenarios

Verify these scenarios work:

### Scenario 1: Create an Event
1. Login as `organizer1`
2. Go to "Create Event"
3. Fill in all details and select a venue
4. Click "Create Event"
5. ✅ Event should be created and appear in "My Events"

### Scenario 2: Venue Conflict Detection
1. Login as `organizer1`
2. Create an event at "College Auditorium" on a specific date/time
3. Try to create another event at the same venue with overlapping time
4. ✅ Should see error: "Venue conflict! This venue already has events: [Event Name]"

### Scenario 3: Register an Attendee
1. Login as `attendee1`
2. Browse events
3. Click "Register Now" on "Python Programming Workshop"
4. ✅ Should see success message and be redirected to event detail
5. ✅ Should see "You are registered for this event!" on the event page

### Scenario 4: Prevent Duplicate Registration
1. Login as `attendee1`
2. Try to register again for "Python Programming Workshop"
3. ✅ Should see error: "You have already registered for this event"

### Scenario 5: Fill Event Capacity
1. Login as `organizer1`
2. Create a new event with capacity = 2
3. Login as `attendee1`, register for the event
4. Login as `attendee2`, register for the event
5. Login as `attendee3`, try to register
6. ✅ Should see: "Event is full! You have been added to the waitlist at position 1."

### Scenario 6: Join Waitlist
1. Login as `attendee3`
2. Try to register for "Annual Tech Conference" (capacity = 3, already full)
3. ✅ Should be added to waitlist at position 1

### Scenario 7: Cancel Registration
1. Login as `attendee1`
2. Go to "Annual Tech Conference" event detail
3. Click "Cancel Registration"
4. ✅ Registration should be cancelled

### Scenario 8: Automatic Waitlist Promotion
1. After cancelling attendee1's registration for "Annual Tech Conference"
2. ✅ attendee4 (position 1 on waitlist) should be automatically promoted
3. ✅ attendee4 should receive a notification about promotion
4. ✅ attendee4 should now have a confirmed registration

### Scenario 9: Generate/View Digital Ticket
1. Login as `attendee1`
2. Go to "My Tickets"
3. Click "View" on any ticket
4. ✅ Should see ticket details with QR code

### Scenario 10: Check In
1. Login as `organizer1`
2. Go to "Annual Tech Conference" event
3. Click "Check-in Attendees"
4. Enter ticket ID (from attendee's ticket)
5. ✅ Should see success message and attendee marked as checked in

### Scenario 11: Certificate Eligibility
1. Login as `attendee1`
2. Go to "Annual Cultural Fest" (completed event)
3. ✅ Should see option to download certificate

### Scenario 12: Generate/Download Certificate
1. Login as `attendee1`
2. Go to "My Certificates"
3. Click "Download" on the certificate
4. ✅ Should download PDF certificate

### Scenario 13: Event Update Notification
1. Login as `organizer1`
2. Edit "Python Programming Workshop" (change date, time, or venue)
3. ✅ All registered attendees should receive notification

### Scenario 14: Add and Assign Vendor
1. Login as `admin` or `organizer1`
2. Go to "Venues" (admin) or create event
3. Add a new vendor
4. Assign vendor to an event
5. ✅ Vendor should appear in event's vendor list

### Scenario 15: Allocate Resources
1. Login as `organizer1`
2. Go to "Python Programming Workshop"
3. Click "Resources" (or similar)
4. Assign resources to the event
5. ✅ Resources should be allocated and venue availability updated

### Scenario 16: Submit Feedback
1. Login as `attendee1`
2. Go to "Annual Cultural Fest" (completed event)
3. Click "Submit Feedback"
4. Fill in rating and comments
5. ✅ Feedback should be submitted and saved

### Scenario 17: View Dashboard Analytics
1. Login as `admin`
2. Go to Admin Dashboard
3. ✅ Should see statistics cards with real data
4. Login as `organizer1`
5. Go to Organizer Dashboard
6. ✅ Should see event statistics and charts

### Scenario 18: Generate Event Report
1. Login as `organizer1`
2. Go to "Python Programming Workshop"
3. View registrations, attendance, etc.
4. ✅ Should see all data based on actual registrations

## 📊 Database Models

### Main Entities
- **User**: Admin, Organizer, Attendee, Vendor
- **Venue**: Event locations with capacity and contact info
- **Event**: Complete event details with status tracking
- **Registration**: Attendee registration for events
- **Waitlist**: Users waiting for spots when events are full
- **Ticket**: Digital tickets with QR codes
- **Attendance**: Check-in records
- **Certificate**: PDF certificates for attendees
- **Vendor**: Service providers
- **Resource**: Equipment and facilities
- **EventVendor**: Many-to-many relationship between events and vendors
- **EventResource**: Many-to-many relationship between events and resources
- **Feedback**: Post-event feedback
- **Notification**: In-app notifications
- **AuditLog**: Track all important actions

## 🎨 UI Features

- ✅ Responsive design (works on desktop, tablet, mobile)
- ✅ Clean, modern Bootstrap 5 interface
- ✅ Consistent navigation and layout
- ✅ Flash messages for user feedback
- ✅ Form validation with helpful error messages
- ✅ Status badges and progress indicators
- ✅ Cards for information display
- ✅ Tables with sorting and pagination (basic)
- ✅ Modal dialogs where appropriate

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///eventsphere.db

# Optional Email (application works without it)
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=noreply@eventsphere.com
MAIL_USE_TLS=1

# File Uploads
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=app/static/uploads
```

## 🚀 Deployment

### Simple Deployment Options

#### Option 1: Render (Recommended)
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables:
   - `SECRET_KEY`: Your secret key
   - `DATABASE_URL`: PostgreSQL connection string from Render
4. Set build command: `pip install -r requirements.txt && flask db upgrade`
5. Set start command: `gunicorn run:app`
6. Deploy!

#### Option 2: PythonAnywhere
1. Create a new Web App
2. Select Flask
3. Upload your code
4. Configure WSGI file
5. Set environment variables
6. Run migrations

#### Option 3: Railway
1. Create a new project
2. Add PostgreSQL service
3. Deploy from GitHub
4. Set environment variables

## 📝 Known Limitations

1. **Email Notifications**: Currently optional. If SMTP is configured, emails will be sent. Otherwise, only in-app notifications work.
2. **REST API**: Basic API endpoints are implemented but not fully comprehensive.
3. **Forecasting**: Not implemented (was optional)
4. **Advanced Analytics**: Basic charts are placeholder; can be enhanced with Chart.js
5. **PostgreSQL**: Configuration supports it, but not fully tested in this version
6. **Mobile App**: Not available; web app is responsive but not a native mobile app

## 🎯 Future Improvements

1. **Enhanced Analytics**: More detailed charts and statistics
2. **Email Templates**: Beautiful HTML email templates
3. **Calendar View**: Visual calendar for events
4. **Advanced Search**: Filter events by multiple criteria
5. **Export Features**: Export reports to Excel/PDF
6. **Bulk Operations**: Bulk import/export users, events, etc.
7. **Multi-language Support**: Internationalization
8. **Two-Factor Authentication**: Enhanced security
9. **API Documentation**: Swagger/OpenAPI documentation
10. **Docker Support**: Containerized deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Commit your changes
6. Push to the branch
7. Create a pull request

## 📄 License

This project is open-source and available for educational purposes.

---

**Built with ❤️ for college project demonstrations**

For questions or issues, please refer to the project documentation or create an issue.
