class Event:
    def __init__(self, event_id, event_name, date, time, venue, resources, status="Planning", attendees=None, vendors=None, capacity=0, waitlist=None):
        self.event_id = event_id
        self.event_name = event_name
        self.date = date
        self.time = time
        self.venue = venue
        self.resources = resources
        self.status = status
        self.attendees = attendees if attendees is not None else []
        self.vendors = vendors if vendors is not None else []
        self.capacity = capacity
        self.waitlist = waitlist if waitlist is not None else []

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "date": self.date,
            "time": self.time,
            "venue": self.venue,
            "resources": self.resources,
            "status": self.status,
            "attendees": self.attendees,
            "vendors": self.vendors,
            "capacity": self.capacity,
            "waitlist": self.waitlist
        }

class Attendee:
    def __init__(self, reg_id, name, email, phone, ticket_id, status="Registered", checkin_time="", certificate="Not Eligible"):
        self.reg_id = reg_id
        self.name = name
        self.email = email
        self.phone = phone
        self.ticket_id = ticket_id
        self.status = status
        self.checkin_time = checkin_time
        self.certificate = certificate

    def to_dict(self):
        return {
            "reg_id": self.reg_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "ticket_id": self.ticket_id,
            "status": self.status,
            "checkin_time": self.checkin_time,
            "certificate": self.certificate
        }

class Vendor:
    def __init__(self, vendor_id, name, service):
        self.vendor_id = vendor_id
        self.name = name
        self.service = service

    def to_dict(self):
        return {
            "vendor_id": self.vendor_id,
            "name": self.name,
            "service": self.service
        }