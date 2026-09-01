from app.models.budget import Budget, Expense, ExpenseStatus
from app.models.approval import ApprovalRequest, ApprovalStatus
from app.models.event import Event
import datetime

def test_expense_auto_approval(app, init_database):
    """Test the expense auto-approval logic."""
    with app.app_context():
        from app.models.user import User
        admin_user = User.query.filter_by(username='admin').first()
        
        from app import db
        
        # Setup event and budget
        event = Event(
            name="Test Event", 
            date=datetime.date(2025, 1, 1), 
            start_time=datetime.time(9, 0),
            end_time=datetime.time(17, 0),
            organizer_id=admin_user.id
        )
        db.session.add(event)
        db.session.commit()
        
        budget = Budget(event_id=event.id, total_amount=100000.0)
        db.session.add(budget)
        db.session.commit()
        
        # Test 1: Expense below threshold
        small_expense = Expense(
            budget_id=budget.id,
            category='catering',
            amount=40000.0,
            description="Snacks",
            requested_by=admin_user.id
        )
        auto_approved, req = small_expense.process_auto_approval(threshold=50000.0)
        assert auto_approved is True
        assert req is None
        assert small_expense.status == ExpenseStatus.APPROVED
        
        # Test 2: Expense above threshold
        large_expense = Expense(
            budget_id=budget.id,
            category='venue',
            amount=60000.0,
            description="Hall booking",
            requested_by=admin_user.id
        )
        auto_approved, req = large_expense.process_auto_approval(threshold=50000.0)
        assert auto_approved is False
        assert req is not None
        assert req.status == ApprovalStatus.PENDING
        assert large_expense.status == ExpenseStatus.PENDING
