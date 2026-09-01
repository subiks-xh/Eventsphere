"""
EventSphere - Optimization Service
"""

from app.models.event import Event, EventStatus
from datetime import datetime, date

class ResourceOptimizer:
    @staticmethod
    def suggest_resource_reuse(resources_needed, start_date, end_date):
        """
        Interval-scheduling algorithm (Activity Selection) to suggest resource reuse 
        across multiple events happening in a given time frame.
        
        Args:
            resources_needed: dict of resource category/name to quantity needed.
            start_date: Start date of the window to check.
            end_date: End date of the window to check.
            
        Returns:
            List of events that can share resources without overlap.
        """
        # Find all upcoming published/open events in this window
        events = Event.query.filter(
            Event.date >= start_date,
            Event.date <= end_date,
            Event.status.in_([EventStatus.PUBLISHED, EventStatus.REGISTRATION_OPEN])
        ).order_by(Event.date, Event.start_time).all()
        
        if not events:
            return []
            
        # Standard interval scheduling (Greedy Activity Selection)
        # Sort events by their end time (date + end_time)
        sorted_events = sorted(events, key=lambda e: datetime.combine(e.date, e.end_time))
        
        selected_events = []
        last_end_time = None
        
        for event in sorted_events:
            current_start_time = datetime.combine(event.date, event.start_time)
            
            # If this event starts after the last selected event ends, we can reuse resources
            if not last_end_time or current_start_time >= last_end_time:
                selected_events.append(event)
                last_end_time = datetime.combine(event.date, event.end_time)
                
        return selected_events
