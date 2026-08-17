class Event:
    def __init__(self, event_id, event_name, date, time, venue, resources, status="Planning"):
        self.event_id = event_id
        self.event_name = event_name
        self.date = date
        self.time = time
        self.venue = venue
        self.resources = resources
        self.status = status

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "date": self.date,
            "time": self.time,
            "venue": self.venue,
            "resources": self.resources,
            "status": self.status
        }