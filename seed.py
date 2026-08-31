"""
EventSphere - Seed Data Generator
Populates the database with demo data for testing and demonstration
"""

import os
from datetime import datetime, date, time, timedelta
from app import create_app, db
from app.models.user import User, UserRole
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


def seed():
    """Seed the database with demo data."""
    app = create_app()
    app.app_context().push()
    
    print("🌱 Seeding EventSphere database...")
    
    # Clear existing data
    print("🧹 Clearing existing data...")
    db.drop_all()
    db.create_all()
    
    # Create Users
    print("👤 Creating users...")
    
    admin = User(
        username='admin',
        email='admin@eventsphere.com',
        password=generate_password_hash('admin123'),
        first_name='Admin',
        last_name='User',
        phone='1234567890',
        role=UserRole.ADMIN
    )
    
    organizer1 = User(
        username='organizer1',
        email='organizer1@eventsphere.com',
        password=generate_password_hash('organizer123'),
        first_name='John',
        last_name='Smith',
        phone='9876543210',
        role=UserRole.ORGANIZER
    )
    
    organizer2 = User(
        username='organizer2',
        email='organizer2@eventsphere.com',
        password=generate_password_hash('organizer123'),
        first_name='Sarah',
        last_name='Johnson',
        phone='5551234567',
        role=UserRole.ORGANIZER
    )
    
    attendee1 = User(
        username='attendee1',
        email='attendee1@eventsphere.com',
        password=generate_password_hash('attendee123'),
        first_name='Alice',
        last_name='Williams',
        phone='1112223333',
        role=UserRole.ATTENDEE
    )
    
    attendee2 = User(
        username='attendee2',
        email='attendee2@eventsphere.com',
        password=generate_password_hash('attendee123'),
        first_name='Bob',
        last_name='Brown',
        phone='4445556666',
        role=UserRole.ATTENDEE
    )
    
    attendee3 = User(
        username='attendee3',
        email='attendee3@eventsphere.com',
        password=generate_password_hash('attendee123'),
        first_name='Charlie',
        last_name='Davis',
        phone='7778889999',
        role=UserRole.ATTENDEE
    )
    
    attendee4 = User(
        username='attendee4',
        email='attendee4@eventsphere.com',
        password=generate_password_hash('attendee123'),
        first_name='Diana',
        last_name='Miller',
        phone='2223334444',
        role=UserRole.ATTENDEE
    )
    
    attendee5 = User(
        username='attendee5',
        email='attendee5@eventsphere.com',
        password=generate_password_hash('attendee123'),
        first_name='Eve',
        last_name='Wilson',
        phone='3334445555',
        role=UserRole.ATTENDEE
    )
    
    vendor1 = User(
        username='vendor1',
        email='vendor1@catering.com',
        password=generate_password_hash('vendor123'),
        first_name='Mike',
        last_name='Chen',
        phone='9998887777',
        role=UserRole.VENDOR
    )
    
    vendor2 = User(
        username='vendor2',
        email='vendor2@decoration.com',
        password=generate_password_hash('vendor123'),
        first_name='Lisa',
        last_name='Garcia',
        phone='6665554444',
        role=UserRole.VENDOR
    )
    
    vendor3 = User(
        username='vendor3',
        email='vendor3@photography.com',
        password=generate_password_hash('vendor123'),
        first_name='Tom',
        last_name='Taylor',
        phone='8889990000',
        role=UserRole.VENDOR
    )
    
    db.session.add_all([
        admin, organizer1, organizer2,
        attendee1, attendee2, attendee3, attendee4, attendee5,
        vendor1, vendor2, vendor3
    ])
    db.session.commit()
    print(f"✅ Created {User.query.count()} users")
    
    # Create Venues
    print("🏢 Creating venues...")
    
    venue1 = Venue(
        name='College Auditorium',
        address='123 University Avenue',
        city='Mumbai',
        state='Maharashtra',
        postal_code='400001',
        country='India',
        capacity=500,
        description='Main auditorium with state-of-the-art audio-visual equipment',
        contact_phone='9876543210',
        contact_email='auditorium@college.edu',
        status='active'
    )
    
    venue2 = Venue(
        name='Seminar Hall A',
        address='456 Campus Road',
        city='Mumbai',
        state='Maharashtra',
        postal_code='400002',
        country='India',
        capacity=100,
        description='Intimate seminar hall perfect for workshops and presentations',
        contact_phone='9876543211',
        contact_email='seminar@college.edu',
        status='active'
    )
    
    venue3 = Venue(
        name='Conference Center',
        address='789 Business District',
        city='Mumbai',
        state='Maharashtra',
        postal_code='400003',
        country='India',
        capacity=200,
        description='Modern conference center with multiple rooms',
        contact_phone='9876543212',
        contact_email='conference@center.com',
        status='active'
    )
    
    venue4 = Venue(
        name='Sports Complex',
        address='321 Athletic Field',
        city='Mumbai',
        state='Maharashtra',
        postal_code='400004',
        country='India',
        capacity=1000,
        description='Large sports complex for outdoor and indoor events',
        contact_phone='9876543213',
        contact_email='sports@complex.com',
        status='active'
    )
    
    db.session.add_all([venue1, venue2, venue3, venue4])
    db.session.commit()
    print(f"✅ Created {Venue.query.count()} venues")
    
    # Create Events
    print("📅 Creating events...")
    
    today = date.today()
    
    # Event 1: Workshop (Organizer 1) - Published with registrations
    event1 = Event(
        name='Python Programming Workshop',
        description='A comprehensive hands-on workshop on Python programming for beginners and intermediate developers.',
        category=EventCategory.WORKSHOP,
        date=today + timedelta(days=15),
        start_time=time(9, 0),
        end_time=time(17, 0),
        venue_id=venue1.id,
        capacity=50,
        registration_deadline=datetime.combine(today + timedelta(days=10), time(23, 59)),
        status=EventStatus.REGISTRATION_OPEN,
        image='https://img.icons8.com/ios/100/007bff/python.png',
        organizer_id=organizer1.id
    )
    
    # Event 2: Seminar (Organizer 1) - Published with registrations
    event2 = Event(
        name='AI and Machine Learning Seminar',
        description='Explore the latest trends and applications in AI and Machine Learning.',
        category=EventCategory.SEMINAR,
        date=today + timedelta(days=20),
        start_time=time(10, 0),
        end_time=time(16, 0),
        venue_id=venue2.id,
        capacity=80,
        registration_deadline=datetime.combine(today + timedelta(days=15), time(23, 59)),
        status=EventStatus.REGISTRATION_OPEN,
        image='https://img.icons8.com/ios/100/007bff/artificial-intelligence.png',
        organizer_id=organizer1.id
    )
    
    # Event 3: Conference (Organizer 2) - Published, full with waitlist
    event3 = Event(
        name='Annual Tech Conference',
        description='The biggest tech conference of the year featuring industry leaders and innovators.',
        category=EventCategory.CONFERENCE,
        date=today + timedelta(days=30),
        start_time=time(8, 0),
        end_time=time(18, 0),
        venue_id=venue3.id,
        capacity=3,  # Small capacity to demonstrate waitlist
        registration_deadline=datetime.combine(today + timedelta(days=25), time(23, 59)),
        status=EventStatus.REGISTRATION_OPEN,
        image='https://img.icons8.com/ios/100/007bff/conference.png',
        organizer_id=organizer2.id
    )
    
    # Event 4: Hackathon (Organizer 2) - Draft
    event4 = Event(
        name='48-Hour Hackathon',
        description='Build innovative projects in 48 hours and win amazing prizes.',
        category=EventCategory.HACKATHON,
        date=today + timedelta(days=45),
        start_time=time(10, 0),
        end_time=time(10, 0),
        venue_id=venue4.id,
        capacity=200,
        registration_deadline=datetime.combine(today + timedelta(days=40), time(23, 59)),
        status=EventStatus.DRAFT,
        image='https://img.icons8.com/ios/100/007bff/hackathon.png',
        organizer_id=organizer2.id
    )
    
    # Event 5: Cultural Event (Organizer 1) - Completed
    event5 = Event(
        name='Annual Cultural Fest',
        description='A celebration of diversity with music, dance, and food from around the world.',
        category=EventCategory.CULTURAL,
        date=today - timedelta(days=5),
        start_time=time(10, 0),
        end_time=time(22, 0),
        venue_id=venue1.id,
        capacity=300,
        registration_deadline=datetime.combine(today - timedelta(days=10), time(23, 59)),
        status=EventStatus.COMPLETED,
        image='https://img.icons8.com/ios/100/007bff/carnival.png',
        organizer_id=organizer1.id
    )
    
    # Event 6: Sports Event (Organizer 2) - Cancelled
    event6 = Event(
        name='Inter-College Football Tournament',
        description='Annual football tournament between colleges.',
        category=EventCategory.SPORTS,
        date=today + timedelta(days=10),
        start_time=time(9, 0),
        end_time=time(17, 0),
        venue_id=venue4.id,
        capacity=500,
        registration_deadline=datetime.combine(today + timedelta(days=5), time(23, 59)),
        status=EventStatus.CANCELLED,
        image='https://img.icons8.com/ios/100/007bff/football2.png',
        organizer_id=organizer2.id
    )
    
    db.session.add_all([event1, event2, event3, event4, event5, event6])
    db.session.commit()
    print(f"✅ Created {Event.query.count()} events")
    
    # Create Registrations
    print("🎫 Creating registrations...")
    
    # Event 1 registrations
    reg1_1 = Registration(
        user_id=attendee1.id,
        event_id=event1.id,
        status=RegistrationStatus.CONFIRMED,
        registration_date=datetime.utcnow() - timedelta(days=5)
    )
    
    reg1_2 = Registration(
        user_id=attendee2.id,
        event_id=event1.id,
        status=RegistrationStatus.CONFIRMED,
        registration_date=datetime.utcnow() - timedelta(days=4)
    )
    
    reg1_3 = Registration(
        user_id=attendee3.id,
        event_id=event1.id,
        status=RegistrationStatus.CONFIRMED,
        registration_date=datetime.utcnow() - timedelta(days=3)
    )
    
    # Event 2 registrations
    reg2_1 = Registration(
        user_id=attendee1.id,
        event_id=event2.id,
        status=RegistrationStatus.CONFIRMED,
        registration_date=datetime.utcnow() - timedelta(days=2)
    )
    
    reg2_2 = Registration(
        user_id=attendee4.id,
        event_id=event2.id,
        status=RegistrationStatus.CONFIRMED,
        registration_date=datetime.utcnow() - timedelta(days=1)
    )
    
    # Event 3 registrations (limited capacity of 3)
    reg3_1 = Registration(
        user_id=attendee1.id,
        event_id=event3.id,
        status=RegistrationStatus.CONFIRMED,
        registration_date=datetime.utcnow() - timedelta(hours=12)
    )
    
    reg3_2 = Registration(
        user_id=attendee2.id,
        event_id=event3.id,
        status=RegistrationStatus.CONFIRMED,
        registration_date=datetime.utcnow() - timedelta(hours=6)
    )
    
    reg3_3 = Registration(
        user_id=attendee3.id,
        event_id=event3.id,
        status=RegistrationStatus.CONFIRMED,
        registration_date=datetime.utcnow() - timedelta(hours=3)
    )
    
    # Event 5 registrations (completed event)
    reg5_1 = Registration(
        user_id=attendee1.id,
        event_id=event5.id,
        status=RegistrationStatus.CONFIRMED,
        registration_date=datetime.utcnow() - timedelta(days=15)
    )
    
    reg5_2 = Registration(
        user_id=attendee2.id,
        event_id=event5.id,
        status=RegistrationStatus.CONFIRMED,
        registration_date=datetime.utcnow() - timedelta(days=12)
    )
    
    reg5_3 = Registration(
        user_id=attendee4.id,
        event_id=event5.id,
        status=RegistrationStatus.CONFIRMED,
        registration_date=datetime.utcnow() - timedelta(days=10)
    )
    
    db.session.add_all([
        reg1_1, reg1_2, reg1_3,
        reg2_1, reg2_2,
        reg3_1, reg3_2, reg3_3,
        reg5_1, reg5_2, reg5_3
    ])
    db.session.commit()
    print(f"✅ Created {Registration.query.count()} registrations")
    
    # Create Tickets
    print("🎟️ Creating tickets...")
    
    ticket1_1 = Ticket(registration=reg1_1)
    ticket1_2 = Ticket(registration=reg1_2)
    ticket1_3 = Ticket(registration=reg1_3)
    ticket2_1 = Ticket(registration=reg2_1)
    ticket2_2 = Ticket(registration=reg2_2)
    ticket3_1 = Ticket(registration=reg3_1)
    ticket3_2 = Ticket(registration=reg3_2)
    ticket3_3 = Ticket(registration=reg3_3)
    ticket5_1 = Ticket(registration=reg5_1)
    ticket5_2 = Ticket(registration=reg5_2)
    ticket5_3 = Ticket(registration=reg5_3)
    
    db.session.add_all([
        ticket1_1, ticket1_2, ticket1_3,
        ticket2_1, ticket2_2,
        ticket3_1, ticket3_2, ticket3_3,
        ticket5_1, ticket5_2, ticket5_3
    ])
    db.session.commit()
    print(f"✅ Created {Ticket.query.count()} tickets")
    
    # Create Waitlist entries for Event 3 (which is full)
    print("⏳ Creating waitlist entries...")
    
    waitlist3_1 = Waitlist(
        event_id=event3.id,
        user_id=attendee4.id,
        position=1,
        joined_at=datetime.utcnow() - timedelta(hours=2)
    )
    
    waitlist3_2 = Waitlist(
        event_id=event3.id,
        user_id=attendee5.id,
        position=2,
        joined_at=datetime.utcnow() - timedelta(hours=1)
    )
    
    db.session.add_all([waitlist3_1, waitlist3_2])
    db.session.commit()
    print(f"✅ Created {Waitlist.query.count()} waitlist entries")
    
    # Create Attendance records for Event 5 (completed)
    print("👥 Creating attendance records...")
    
    att5_1 = Attendance(
        registration_id=reg5_1.id,
        check_in_time=datetime.combine(event5.date, time(10, 30)),
        check_in_method='qr_code'
    )
    
    att5_2 = Attendance(
        registration_id=reg5_2.id,
        check_in_time=datetime.combine(event5.date, time(11, 0)),
        check_in_method='manual'
    )
    
    att5_3 = Attendance(
        registration_id=reg5_3.id,
        check_in_time=datetime.combine(event5.date, time(12, 15)),
        check_in_method='qr_code'
    )
    
    db.session.add_all([att5_1, att5_2, att5_3])
    db.session.commit()
    print(f"✅ Created {Attendance.query.count()} attendance records")
    
    # Create Certificates for Event 5 attendees
    print("🏆 Creating certificates...")
    
    cert5_1 = Certificate(registration=reg5_1)
    cert5_2 = Certificate(registration=reg5_2)
    cert5_3 = Certificate(registration=reg5_3)
    
    db.session.add_all([cert5_1, cert5_2, cert5_3])
    db.session.commit()
    print(f"✅ Created {Certificate.query.count()} certificates")
    
    # Create Vendors
    print("🛒 Creating vendors...")
    
    vendor_profile1 = Vendor(
        user_id=vendor1.id,
        business_name='Delicious Catering Services',
        contact_person='Mike Chen',
        email='mike@catering.com',
        phone='9876543210',
        service=VendorService.CATERING,
        description='Premium catering services for events of all sizes',
        address='101 Food Street, Mumbai',
        status='active'
    )
    
    vendor_profile2 = Vendor(
        user_id=vendor2.id,
        business_name='Elegant Decorators',
        contact_person='Lisa Garcia',
        email='lisa@decorators.com',
        phone='9876543211',
        service=VendorService.DECORATION,
        description='Beautiful decorations for weddings, conferences, and parties',
        address='202 Design Avenue, Mumbai',
        status='active'
    )
    
    vendor_profile3 = Vendor(
        user_id=vendor3.id,
        business_name='Professional Photography',
        contact_person='Tom Taylor',
        email='tom@photography.com',
        phone='9876543212',
        service=VendorService.PHOTOGRAPHY,
        description='High-quality photography and videography services',
        address='303 Photo Lane, Mumbai',
        status='active'
    )
    
    db.session.add_all([vendor_profile1, vendor_profile2, vendor_profile3])
    db.session.commit()
    print(f"✅ Created {Vendor.query.count()} vendor profiles")
    
    # Create Resources
    print("📦 Creating resources...")
    
    resource1 = Resource(
        name='Projector',
        description='High-definition projector with HDMI and VGA inputs',
        category='Audio/Visual',
        total_quantity=10,
        available_quantity=8,
        status='available'
    )
    
    resource2 = Resource(
        name='Microphone',
        description='Wireless microphone system',
        category='Audio/Visual',
        total_quantity=20,
        available_quantity=15,
        status='available'
    )
    
    resource3 = Resource(
        name='Whiteboard',
        description='Large mobile whiteboard with markers',
        category='Presentation',
        total_quantity=5,
        available_quantity=3,
        status='available'
    )
    
    resource4 = Resource(
        name='Chairs',
        description='Folding chairs for event seating',
        category='Furniture',
        total_quantity=500,
        available_quantity=450,
        status='available'
    )
    
    resource5 = Resource(
        name='Tables',
        description='Round tables for conferences and meetings',
        category='Furniture',
        total_quantity=50,
        available_quantity=40,
        status='available'
    )
    
    db.session.add_all([resource1, resource2, resource3, resource4, resource5])
    db.session.commit()
    print(f"✅ Created {Resource.query.count()} resources")
    
    # Create Event-Vendor assignments
    print("🔗 Creating event-vendor assignments...")
    
    ev1 = EventVendor(
        event_id=event1.id,
        vendor_id=vendor_profile1.id,
        service='catering',
        requirements='Vegetarian and non-vegetarian options, snacks, and beverages',
        status='confirmed'
    )
    
    ev2 = EventVendor(
        event_id=event2.id,
        vendor_id=vendor_profile2.id,
        service='decoration',
        requirements='Stage decoration, banners, and table arrangements',
        status='pending'
    )
    
    ev3 = EventVendor(
        event_id=event5.id,
        vendor_id=vendor_profile3.id,
        service='photography',
        requirements='Event coverage, group photos, and individual portraits',
        status='completed'
    )
    
    db.session.add_all([ev1, ev2, ev3])
    db.session.commit()
    print(f"✅ Created {EventVendor.query.count()} event-vendor assignments")
    
    # Create Event-Resource assignments
    print("🔧 Creating event-resource assignments...")
    
    er1 = EventResource(
        event_id=event1.id,
        resource_id=resource1.id,
        quantity=2
    )
    
    er2 = EventResource(
        event_id=event1.id,
        resource_id=resource2.id,
        quantity=3
    )
    
    er3 = EventResource(
        event_id=event2.id,
        resource_id=resource1.id,
        quantity=1
    )
    
    er4 = EventResource(
        event_id=event5.id,
        resource_id=resource4.id,
        quantity=100
    )
    
    er5 = EventResource(
        event_id=event5.id,
        resource_id=resource5.id,
        quantity=20
    )
    
    db.session.add_all([er1, er2, er3, er4, er5])
    db.session.commit()
    print(f"✅ Created {EventResource.query.count()} event-resource assignments")
    
    # Create Feedback for Event 5
    print("💬 Creating feedback...")
    
    feedback1 = Feedback(
        registration_id=reg5_1.id,
        user_id=attendee1.id,
        event_id=event5.id,
        rating=5,
        comments='Amazing event! The cultural performances were outstanding.',
        suggestions='More food stalls would be great.'
    )
    
    feedback2 = Feedback(
        registration_id=reg5_2.id,
        user_id=attendee2.id,
        event_id=event5.id,
        rating=4,
        comments='Great organization and wonderful atmosphere.',
        suggestions='Better parking arrangements needed.'
    )
    
    db.session.add_all([feedback1, feedback2])
    db.session.commit()
    print(f"✅ Created {Feedback.query.count()} feedback entries")
    
    # Create Notifications
    print("🔔 Creating notifications...")
    
    # Registration notifications
    not1 = Notification(
        user_id=attendee1.id,
        message=f'You have successfully registered for "{event1.name}"!',
        type=NotificationType.REGISTRATION,
        data={'event_id': event1.id}
    )
    
    not2 = Notification(
        user_id=attendee1.id,
        message=f'Your ticket for "{event1.name}" has been generated.',
        type=NotificationType.TICKET,
        data={'ticket_id': ticket1_1.id}
    )
    
    not3 = Notification(
        user_id=attendee1.id,
        message=f'You have been checked in for "{event5.name}".',
        type=NotificationType.CHECKIN,
        data={'event_id': event5.id}
    )
    
    not4 = Notification(
        user_id=attendee1.id,
        message=f'Your certificate for "{event5.name}" is now available!',
        type=NotificationType.CERTIFICATE_AVAILABLE,
        data={'certificate_id': cert5_1.id}
    )
    
    # Waitlist notification
    not5 = Notification(
        user_id=attendee4.id,
        message=f'You have been added to the waitlist for "{event3.name}". Position: 1',
        type=NotificationType.WAITLIST,
        data={'event_id': event3.id, 'position': 1}
    )
    
    db.session.add_all([not1, not2, not3, not4, not5])
    db.session.commit()
    print(f"✅ Created {Notification.query.count()} notifications")
    
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
    print(f"   Notifications: {Notification.query.count()}")
    
    print(f"\n👤 Demo Accounts:")
    print(f"   Admin: admin / admin123")
    print(f"   Organizer 1: organizer1 / organizer123")
    print(f"   Organizer 2: organizer2 / organizer123")
    print(f"   Attendee 1: attendee1 / attendee123")
    print(f"   Attendee 2: attendee2 / attendee123")
    print(f"   Vendor 1: vendor1 / vendor123")
    
    print(f"\n🚀 Run the application with: flask run")
    print(f"   Then visit: http://127.0.0.1:5000")


if __name__ == '__main__':
    seed()
