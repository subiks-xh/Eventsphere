"""
EventSphere - Badges Utility
Calculates gamification badges for users based on their activity.
"""

def compute_badges(user):
    """
    Compute gamification badges for a user.
    
    Returns a list of badge dictionaries:
    [{'id': 'first_timer', 'name': 'First Timer', 'icon': 'bi-star', 'color': 'warning', 'description': '...'}]
    """
    badges = []
    
    # Needs attendance, registrations, feedback counts
    
    # 1. First Timer — First event registration
    if user.registrations:
        badges.append({
            'id': 'first_timer',
            'name': 'First Timer',
            'icon': 'bi-ticket-detailed',
            'color': 'info',
            'description': 'Registered for your first event!'
        })
        
    # 2. Event Regular — Attended 3+ events (Multi-tier)
    attended = user.attended_events_count
    if attended >= 25:
        badges.append({
            'id': 'event_regular_gold', 'name': 'Event Regular (Gold)', 'icon': 'bi-trophy-fill',
            'color': '#FFD700', 'description': 'Attended 25+ events!'
        })
    elif attended >= 10:
        badges.append({
            'id': 'event_regular_silver', 'name': 'Event Regular (Silver)', 'icon': 'bi-trophy',
            'color': '#C0C0C0', 'description': 'Attended 10+ events.'
        })
    elif attended >= 3:
        badges.append({
            'id': 'event_regular_bronze', 'name': 'Event Regular (Bronze)', 'icon': 'bi-award',
            'color': '#cd7f32', 'description': 'Attended 3+ events.'
        })
        
    # 3. Feedback Champion — Submitted feedback (Multi-tier)
    feedback_count = user.feedback_count
    if feedback_count >= 25:
        badges.append({
            'id': 'feedback_champion_gold', 'name': 'Feedback Champion (Gold)', 'icon': 'bi-chat-heart-fill',
            'color': '#FFD700', 'description': 'Submitted 25+ feedback entries!'
        })
    elif feedback_count >= 10:
        badges.append({
            'id': 'feedback_champion_silver', 'name': 'Feedback Champion (Silver)', 'icon': 'bi-chat-heart',
            'color': '#C0C0C0', 'description': 'Submitted 10+ feedback entries.'
        })
    elif feedback_count >= 3:
        badges.append({
            'id': 'feedback_champion_bronze', 'name': 'Feedback Champion (Bronze)', 'icon': 'bi-chat-heart',
            'color': '#cd7f32', 'description': 'Submitted 3+ feedback entries.'
        })
        
    # 4. Perfect Attendee — Attended every event they registered for (min 2)
    completed_registrations = [r for r in user.registrations if r.event and r.event.status == 'completed']
    if len(completed_registrations) >= 2:
        actually_attended = sum(1 for r in completed_registrations if r.has_checked_in)
        if actually_attended == len(completed_registrations):
            badges.append({
                'id': 'perfect_attendee',
                'name': 'Perfect Attendee',
                'icon': 'bi-stars',
                'color': 'warning',
                'description': '100% attendance rate for completed events!'
            })
            
    # 5. Early Bird - Registered within 24h of an event opening
    is_early_bird = False
    for reg in user.registrations:
        if reg.event and reg.event.created_at:
            diff = reg.registration_date - reg.event.created_at
            if diff.total_seconds() <= 86400:  # 24 hours
                is_early_bird = True
                break
                
    if is_early_bird:
        badges.append({
            'id': 'early_bird',
            'name': 'Early Bird',
            'icon': 'bi-lightning',
            'color': 'danger',
            'description': 'Registered within 24 hours of an event opening.'
        })
        
    return badges
