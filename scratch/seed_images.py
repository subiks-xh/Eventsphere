import os
import sys

# Add the project root to the path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.event import Event, EventCategory

app = create_app()

def seed_images():
    with app.app_context():
        events = Event.query.all()
        for event in events:
            if event.category in [EventCategory.WORKSHOP, EventCategory.SEMINAR, EventCategory.TECHNICAL]:
                event.image = 'tech.jpg'
            elif event.category == EventCategory.HACKATHON:
                event.image = 'hackathon.jpg'
            elif event.category in [EventCategory.CULTURAL, EventCategory.SPORTS, EventCategory.OTHER]:
                event.image = 'cultural.jpg'
            else:
                event.image = 'tech.jpg'
        db.session.commit()
        print(f"Updated {len(events)} events with images.")

if __name__ == '__main__':
    seed_images()
