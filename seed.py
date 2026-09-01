"""
EventSphere - Seed Data Generator
Populates the database with demo data for testing and demonstration
"""

import os
import random
from datetime import datetime, date, time, timedelta
from app import create_app, db
from app.models.user import User, UserRole, UserStatus
from app.models.venue import Venue
from app.models.event import Event, EventCategory, EventStatus
from app.models.registration import Registration, RegistrationStatus
from app.models.ticket import Ticket
from app.models.waitlist import Waitlist, WaitlistStatus
from app.models.vendor import Vendor, VendorService
from app.models.resource import Resource
from app.models.event_resource import EventResource
from app.models.event_vendor import EventVendor, EventVendorStatus
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.models.feedback import Feedback
from app.models.notification import Notification, NotificationType
from werkzeug.security import generate_password_hash
try:
    from faker import Faker
except ImportError:
    print("Please install faker: pip install faker")
    exit(1)


def seed():
    """Seed the database with demo data."""
    app = create_app()
    app.app_context().push()
    fake = Faker()
    
    print("🌱 Seeding EventSphere database...")
    print("🧹 Clearing existing data...")
    db.drop_all()
    db.create_all()
    
    # 1. Create Base Admin & Organizers
    print("👤 Creating admin and organizers...")
    admin = User(
        username='admin', email='admin@eventsphere.com',
        password='admin123',
        first_name='Admin', last_name='User', phone='1234567890', role=UserRole.ADMIN
    )
    
    organizers = []
    for i in range(1, 11):
        org = User(
            username=f'organizer{i}', email=f'organizer{i}@eventsphere.com',
            password='organizer123',
            first_name=fake.first_name(), last_name=fake.last_name(),
            phone=fake.phone_number()[:20], role=UserRole.ORGANIZER
        )
        organizers.append(org)
    
    # 2. Create 500+ Attendees
    print(f"👥 Creating 500 attendees...")
    attendees = []
    for i in range(1, 501):
        att = User(
            username=f'attendee{i}_{fake.user_name()}'[:80],
            email=f'attendee{i}_{fake.email()}'[:120],
            password='attendee123',
            first_name=fake.first_name(), last_name=fake.last_name(),
            phone=fake.phone_number()[:20], role=UserRole.ATTENDEE
        )
        attendees.append(att)

    # 3. Create 20 Vendors
    print("🛒 Creating 20 vendors...")
    vendor_users = []
    vendor_profiles = []
    services = [VendorService.CATERING, VendorService.DECORATION, VendorService.PHOTOGRAPHY, VendorService.SECURITY, VendorService.AUDIO_VISUAL, VendorService.OTHER]
    
    for i in range(1, 21):
        v_user = User(
            username=f'vendor{i}_{fake.user_name()}'[:80],
            email=f'vendor{i}_{fake.email()}'[:120],
            password='vendor123',
            first_name=fake.first_name(), last_name=fake.last_name(),
            phone=fake.phone_number()[:20], role=UserRole.VENDOR
        )
        vendor_users.append(v_user)

    db.session.add(admin)
    db.session.add_all(organizers)
    db.session.add_all(attendees)
    db.session.add_all(vendor_users)
    db.session.commit()

    for i, v_user in enumerate(vendor_users):
        v_prof = Vendor(
            user_id=v_user.id,
            business_name=fake.company(),
            contact_person=f"{v_user.first_name} {v_user.last_name}",
            email=v_user.email,
            phone=v_user.phone,
            service=random.choice(services),
            description=fake.bs(),
            address=fake.address(),
            status='active'
        )
        vendor_profiles.append(v_prof)
    db.session.add_all(vendor_profiles)
    db.session.commit()

    # 4. Create Venues
    print("🏢 Creating venues...")
    venues = []
    for i in range(1, 16):
        v = Venue(
            name=f"{fake.company()} {random.choice(['Hall', 'Center', 'Auditorium', 'Arena'])}",
            address=fake.street_address(),
            city=fake.city(),
            state=fake.state(),
            postal_code=fake.zipcode()[:10],
            country=fake.country()[:50],
            capacity=random.randint(50, 1000),
            description=fake.text(max_nb_chars=200),
            contact_phone=fake.phone_number()[:20],
            contact_email=fake.company_email(),
            status='active'
        )
        venues.append(v)
    db.session.add_all(venues)
    db.session.commit()
    
    # 5. Create 100+ Events
    print("📅 Creating 120 events...")
    events = []
    categories = [EventCategory.WORKSHOP, EventCategory.SEMINAR, EventCategory.CONFERENCE, EventCategory.HACKATHON, EventCategory.CULTURAL, EventCategory.SPORTS, EventCategory.TECHNICAL, EventCategory.OTHER]
    statuses = [EventStatus.DRAFT, EventStatus.PUBLISHED, EventStatus.REGISTRATION_OPEN, EventStatus.REGISTRATION_CLOSED, EventStatus.ONGOING, EventStatus.COMPLETED, EventStatus.CANCELLED]
    
    today = date.today()
    for i in range(1, 121):
        event_date = today + timedelta(days=random.randint(-60, 120))
        # Decide status based on date
        if event_date < today:
            status = random.choice([EventStatus.COMPLETED, EventStatus.CANCELLED])
        elif event_date == today:
            status = EventStatus.ONGOING
        else:
            status = random.choice([EventStatus.PUBLISHED, EventStatus.REGISTRATION_OPEN, EventStatus.DRAFT, EventStatus.REGISTRATION_CLOSED])

        start_h = random.randint(8, 16)
        ev = Event(
            name=fake.catch_phrase(),
            description=fake.text(max_nb_chars=500),
            category=random.choice(categories),
            date=event_date,
            start_time=time(start_h, 0),
            end_time=time(start_h + random.randint(2, 6), 0),
            venue_id=random.choice(venues).id,
            capacity=random.randint(50, 500),
            registration_deadline=datetime.combine(event_date - timedelta(days=2), time(23, 59)),
            status=status,
            organizer_id=random.choice(organizers).id
        )
        events.append(ev)
    db.session.add_all(events)
    db.session.commit()

    # 6. Resources
    print("📦 Creating resources...")
    resources = []
    for i in range(1, 21):
        res = Resource(
            name=fake.word().capitalize() + f" Equipment {i}",
            description=fake.sentence(),
            category=random.choice(['Audio/Visual', 'Presentation', 'Furniture']),
            total_quantity=random.randint(20, 100),
            available_quantity=random.randint(10, 50),
            status='available'
        )
        resources.append(res)
    db.session.add_all(resources)
    db.session.commit()

    # 7. Registrations, Tickets, Waitlist, Attendance, Feedback
    print("🎫 Simulating registrations, waitlists, and attendance for events...")
    
    # We will loop through a portion of events and add random attendees
    all_attendee_ids = [a.id for a in attendees]
    
    for ev in events:
        if ev.status in [EventStatus.DRAFT, EventStatus.PUBLISHED]:
            continue
            
        num_regs = random.randint(10, min(ev.capacity + 20, 100)) # Cap at 100 for speed
        sampled_user_ids = random.sample(all_attendee_ids, num_regs)
        
        current_confirmed = 0
        
        for uid in sampled_user_ids:
            if current_confirmed < ev.capacity:
                # Register
                reg = Registration(
                    user_id=uid,
                    event_id=ev.id,
                    status=RegistrationStatus.CONFIRMED,
                    registration_date=datetime.utcnow() - timedelta(days=random.randint(1, 10))
                )
                db.session.add(reg)
                db.session.commit() # commit to get ID
                current_confirmed += 1
                
                # Ticket
                ticket = Ticket(registration=reg)
                db.session.add(ticket)
                
                # Attendance & Feedback if completed
                if ev.status == EventStatus.COMPLETED:
                    if random.random() > 0.1: # 90% attendance
                        att = Attendance(
                            registration_id=reg.id,
                            check_in_time=datetime.combine(ev.date, ev.start_time) + timedelta(minutes=random.randint(0, 30)),
                            check_in_method='qr_code'
                        )
                        db.session.add(att)
                        
                        # Generate certificate
                        cert = Certificate(registration=reg)
                        db.session.add(cert)
                        
                        # Generate feedback (40% chance)
                        if random.random() > 0.6:
                            fb = Feedback(
                                registration_id=reg.id,
                                user_id=uid,
                                event_id=ev.id,
                                rating=random.randint(3, 5),
                                comments=fake.sentence()
                            )
                            db.session.add(fb)
            else:
                # Waitlist
                wl = Waitlist(
                    event_id=ev.id,
                    user_id=uid,
                    position=current_confirmed - ev.capacity + 1,
                    status='active'
                )
                db.session.add(wl)
                current_confirmed += 1

    db.session.commit()
    
    print("\n" + "="*60)
    print("🎉 SEEDING COMPLETE!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"   Users: {User.query.count()}")
    print(f"   Venues: {Venue.query.count()}")
    print(f"   Events: {Event.query.count()}")
    print(f"   Registrations: {Registration.query.count()}")
    print(f"   Tickets: {Ticket.query.count()}")
    print(f"   Waitlist: {Waitlist.query.count()}")
    print(f"   Vendors: {Vendor.query.count()}")
    print(f"   Resources: {Resource.query.count()}")
    print(f"   Feedback: {Feedback.query.count()}")
    
    print(f"\n👤 Demo Accounts:")
    print(f"   Admin: admin / admin123")
    print(f"   Organizer 1: organizer1 / organizer123")
    print(f"   Attendee 1: attendee1_... / attendee123")
    
if __name__ == '__main__':
    seed()
