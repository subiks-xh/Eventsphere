"""
EventSphere - Forecasting Service
"""

from app.models.event import Event, EventStatus
from app.models.registration import Registration, RegistrationStatus
from app.models.attendance import Attendance
from app import db

class AttendanceForecaster:
    @staticmethod
    def forecast_attendance(category, capacity, organizer_id=None):
        """
        Forecast expected attendance for a new event based on historical moving average
        of similar past events (same category and/or same organizer).
        """
        query = Event.query.filter(Event.status == EventStatus.COMPLETED)
        
        if organizer_id:
            query = query.filter(Event.organizer_id == organizer_id)
            
        if category:
            query = query.filter(Event.category == category)
            
        # Get up to 10 most recent completed events matching criteria
        past_events = query.order_by(Event.date.desc()).limit(10).all()
        
        if not past_events:
            # If no history, assume 75% of capacity as a baseline naive forecast
            return int(capacity * 0.75) if capacity else 0
            
        total_attendance_rate = 0.0
        events_counted = 0
        
        for e in past_events:
            if e.capacity and e.capacity > 0:
                # Calculate attendance rate relative to capacity
                atts = Attendance.query.join(Registration).filter(Registration.event_id == e.id).count()
                rate = atts / e.capacity
                total_attendance_rate += rate
                events_counted += 1
                
        if events_counted == 0:
            return int(capacity * 0.75) if capacity else 0
            
        avg_rate = total_attendance_rate / events_counted
        
        # Apply the average rate to the new capacity
        forecast = int(capacity * avg_rate) if capacity else 0
        return forecast
