"""
EventSphere - Analytics Service
"""

from app.models.event import Event, EventStatus
from app.models.registration import Registration, RegistrationStatus
from app.models.attendance import Attendance
from app.models.budget import Budget, Expense, Sponsorship
from sqlalchemy import func
from app import db

class EventAnalytics:
    @staticmethod
    def get_organizer_kpis(organizer_id):
        """Calculate high-level KPIs for an organizer's dashboard."""
        
        # Base event query
        events_query = Event.query.filter_by(organizer_id=organizer_id)
        total_events = events_query.count()
        
        # Registrations and Attendance
        total_registrations = Registration.query.join(Event).filter(
            Event.organizer_id == organizer_id,
            Registration.status == RegistrationStatus.CONFIRMED
        ).count()
        
        total_attendance = Attendance.query.join(Registration).join(Event).filter(
            Event.organizer_id == organizer_id
        ).count()
        
        # Financials (Budgets & Expenses)
        budgets = Budget.query.join(Event).filter(Event.organizer_id == organizer_id).all()
        total_budget_allocated = sum(b.total_amount for b in budgets)
        total_expenses_approved = sum(b.approved_expenses_total for b in budgets)
        
        utilization_rate = 0
        if total_budget_allocated > 0:
            utilization_rate = (total_expenses_approved / total_budget_allocated) * 100
            
        # Attendance Rate
        attendance_rate = 0
        if total_registrations > 0:
            attendance_rate = (total_attendance / total_registrations) * 100
            
        return {
            'total_events': total_events,
            'total_registrations': total_registrations,
            'total_attendance': total_attendance,
            'attendance_rate': attendance_rate,
            'total_budget': total_budget_allocated,
            'total_expenses': total_expenses_approved,
            'utilization_rate': utilization_rate
        }
        
    @staticmethod
    def get_attendance_trends(organizer_id, limit=5):
        """Get attendance vs registration data for recent completed events."""
        completed_events = Event.query.filter(
            Event.organizer_id == organizer_id,
            Event.status == EventStatus.COMPLETED
        ).order_by(Event.date.desc()).limit(limit).all()
        
        # Reverse to chronological order
        completed_events.reverse()
        
        labels = []
        registrations = []
        attendance = []
        
        for e in completed_events:
            labels.append(e.name[:15] + '...' if len(e.name) > 15 else e.name)
            regs = Registration.query.filter_by(event_id=e.id, status=RegistrationStatus.CONFIRMED).count()
            atts = Attendance.query.join(Registration).filter(Registration.event_id == e.id).count()
            registrations.append(regs)
            attendance.append(atts)
            
        return {
            'labels': labels,
            'registrations': registrations,
            'attendance': attendance
        }
        
    @staticmethod
    def get_budget_distribution(organizer_id):
        """Get breakdown of expenses by category across all events."""
        expenses = db.session.query(
            Expense.category, func.sum(Expense.amount).label('total')
        ).join(Budget).join(Event).filter(
            Event.organizer_id == organizer_id,
            Expense.status == 'approved'
        ).group_by(Expense.category).all()
        
        labels = [e.category.title() for e in expenses]
        data = [float(e.total) for e in expenses]
        
        return {
            'labels': labels,
            'data': data
        }
