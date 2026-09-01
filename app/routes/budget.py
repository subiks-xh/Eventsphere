"""
EventSphere - Budget & Sponsorship Routes
"""

from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.event import Event
from app.models.budget import Budget, Expense, Sponsorship, ExpenseStatus
from app.models.approval import ApprovalRequest, ApprovalStatus
from app.models.notification import Notification, NotificationType
from app.models.audit_log import AuditLog
from app.forms.budget import BudgetForm, ExpenseForm, SponsorshipForm, ApprovalActionForm

budget_bp = Blueprint('budget', __name__, url_prefix='/organizer')

def check_organizer_or_admin(event):
    """Check if current user is the event organizer or an admin."""
    if current_user.id != event.organizer_id and not current_user.is_admin:
        abort(403)

@budget_bp.route('/events/<int:event_id>/budget', methods=['GET', 'POST'])
@login_required
def dashboard(event_id):
    """Budget dashboard for an event."""
    event = Event.query.get_or_404(event_id)
    check_organizer_or_admin(event)
    
    # Get or create budget
    budget = event.budget
    if not budget:
        budget = Budget(event_id=event.id, total_amount=0.0)
        db.session.add(budget)
        db.session.commit()
        
    budget_form = BudgetForm(obj=budget)
    expense_form = ExpenseForm()
    sponsorship_form = SponsorshipForm()
    
    # Handle Budget Update
    if 'update_budget' in request.form and budget_form.validate_on_submit():
        budget.total_amount = budget_form.total_amount.data
        db.session.commit()
        
        AuditLog.log_action(
            user_id=current_user.id,
            action='update_budget',
            entity='budget',
            entity_id=budget.id,
            details=f"Updated budget for event {event.name} to {budget.total_amount}",
            request=request
        )
        flash('Budget updated successfully.', 'success')
        return redirect(url_for('budget.dashboard', event_id=event.id))
        
    # Stats for UI
    total_sponsorship = sum(s.amount for s in event.sponsorships)
    net_position = total_sponsorship - budget.approved_expenses_total
    
    # Get all expenses ordered by latest
    expenses = Expense.query.filter_by(budget_id=budget.id).order_by(Expense.created_at.desc()).all()
    
    return render_template(
        'organizer/budget/dashboard.html',
        event=event,
        budget=budget,
        expenses=expenses,
        sponsorships=event.sponsorships,
        total_sponsorship=total_sponsorship,
        net_position=net_position,
        budget_form=budget_form,
        expense_form=expense_form,
        sponsorship_form=sponsorship_form,
        title=f'Budget - {event.name}'
    )

@budget_bp.route('/events/<int:event_id>/budget/expense', methods=['POST'])
@login_required
def add_expense(event_id):
    """Add a new expense."""
    event = Event.query.get_or_404(event_id)
    check_organizer_or_admin(event)
    
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            budget_id=event.budget.id,
            category=form.category.data,
            amount=form.amount.data,
            description=form.description.data,
            requested_by=current_user.id
        )
        
        # Process auto-approval logic threshold (e.g. 50,000)
        auto_approved, approval_req = expense.process_auto_approval(threshold=50000.0)
        
        db.session.add(expense)
        db.session.commit() # commit to get expense.id
        
        if not auto_approved and approval_req:
            approval_req.expense_id = expense.id
            db.session.add(approval_req)
            db.session.commit()
            
            # Notify admins or event organizer
            AuditLog.log_action(
                user_id=current_user.id,
                action='create_expense_approval',
                entity='expense',
                entity_id=expense.id,
                details=f"Created expense requiring approval for {event.name} ({expense.amount})",
                request=request
            )
            flash('Expense exceeds threshold. An approval request has been submitted.', 'info')
        else:
            expense.approved_by = current_user.id
            db.session.commit()
            AuditLog.log_action(
                user_id=current_user.id,
                action='add_expense',
                entity='expense',
                entity_id=expense.id,
                details=f"Auto-approved expense for {event.name} ({expense.amount})",
                request=request
            )
            flash('Expense recorded and auto-approved.', 'success')
            
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
                
    return redirect(url_for('budget.dashboard', event_id=event.id))


@budget_bp.route('/events/<int:event_id>/budget/sponsorship', methods=['POST'])
@login_required
def add_sponsorship(event_id):
    """Add a new sponsorship."""
    event = Event.query.get_or_404(event_id)
    check_organizer_or_admin(event)
    
    form = SponsorshipForm()
    if form.validate_on_submit():
        sponsorship = Sponsorship(
            event_id=event.id,
            sponsor_name=form.sponsor_name.data,
            amount=form.amount.data,
            contact_email=form.contact_email.data
        )
        db.session.add(sponsorship)
        db.session.commit()
        
        AuditLog.log_action(
            user_id=current_user.id,
            action='add_sponsorship',
            entity='sponsorship',
            entity_id=sponsorship.id,
            details=f"Added sponsorship {sponsorship.sponsor_name} to event {event.name}",
            request=request
        )
        flash('Sponsorship added successfully.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
                
    return redirect(url_for('budget.dashboard', event_id=event.id))


@budget_bp.route('/approvals', methods=['GET'])
@login_required
def approvals_inbox():
    """Inbox for pending approval requests."""
    # Admins see all pending requests; Organizers see requests for their events
    if current_user.is_admin:
        pending_requests = ApprovalRequest.query.filter_by(status=ApprovalStatus.PENDING).all()
    elif current_user.is_organizer:
        pending_requests = ApprovalRequest.query.join(Expense).join(Budget).join(Event).filter(
            Event.organizer_id == current_user.id,
            ApprovalRequest.status == ApprovalStatus.PENDING
        ).all()
    else:
        abort(403)
        
    form = ApprovalActionForm()
    return render_template(
        'organizer/budget/approvals.html',
        pending_requests=pending_requests,
        form=form,
        title='Approval Inbox'
    )


@budget_bp.route('/approvals/<int:request_id>/process', methods=['POST'])
@login_required
def process_approval(request_id):
    """Process an approval request (Approve/Reject)."""
    approval = ApprovalRequest.query.get_or_404(request_id)
    expense = approval.expense
    event = expense.budget.event
    
    # Auth check
    if not current_user.is_admin and current_user.id != event.organizer_id:
        abort(403)
        
    # State enforcement
    if approval.status != ApprovalStatus.PENDING:
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('budget.approvals_inbox'))
        
    form = ApprovalActionForm()
    if form.validate_on_submit():
        action = form.action.data
        notes = form.notes.data
        
        if action == 'approve':
            approval.status = ApprovalStatus.APPROVED
            expense.status = ExpenseStatus.APPROVED
            expense.approved_by = current_user.id
            flash_msg = 'Expense approved successfully.'
        elif action == 'reject':
            approval.status = ApprovalStatus.REJECTED
            expense.status = ExpenseStatus.REJECTED
            flash_msg = 'Expense rejected.'
            
        approval.resolved_at = datetime.utcnow()
        approval.resolver_id = current_user.id
        approval.notes = notes
        
        db.session.commit()
        
        # Notify the requester
        if expense.requested_by != current_user.id:
            notif = Notification(
                user_id=expense.requested_by,
                title=f"Expense {action.capitalize()}",
                message=f"Your expense of ₹{expense.amount} for {event.name} has been {action}d.",
                type=NotificationType.SYSTEM,
                link=url_for('budget.dashboard', event_id=event.id)
            )
            db.session.add(notif)
            db.session.commit()
            
        AuditLog.log_action(
            user_id=current_user.id,
            action=f'process_approval_{action}',
            entity='approval_request',
            entity_id=approval.id,
            details=f"Processed approval for expense {expense.id} -> {action}",
            request=request
        )
        flash(flash_msg, 'success')
    else:
        flash('Invalid action.', 'danger')
        
    return redirect(url_for('budget.approvals_inbox'))

@budget_bp.route('/events/<int:event_id>/budget/export', methods=['GET'])
@login_required
def export_budget(event_id):
    """Export budget and expenses as CSV."""
    import csv
    from io import StringIO
    from flask import Response
    
    event = Event.query.get_or_404(event_id)
    check_organizer_or_admin(event)
    
    budget = event.budget
    if not budget:
        flash('No budget data to export.', 'warning')
        return redirect(url_for('budget.dashboard', event_id=event.id))
        
    # Create CSV in memory
    si = StringIO()
    cw = csv.writer(si)
    
    # Write summary
    cw.writerow(['Budget Summary'])
    cw.writerow(['Event Name', event.name])
    cw.writerow(['Total Budget Allocated', budget.total_amount])
    cw.writerow(['Total Approved Expenses', budget.approved_expenses_total])
    cw.writerow(['Remaining Budget', budget.remaining_budget])
    cw.writerow([])
    
    # Write expenses
    cw.writerow(['Expenses List'])
    cw.writerow(['ID', 'Category', 'Amount', 'Status', 'Description', 'Requested By', 'Created At'])
    
    expenses = Expense.query.filter_by(budget_id=budget.id).order_by(Expense.created_at.desc()).all()
    for exp in expenses:
        cw.writerow([
            exp.id,
            exp.category,
            exp.amount,
            exp.status,
            exp.description,
            exp.requester.username if exp.requester else 'Unknown',
            exp.created_at.strftime('%Y-%m-%d %H:%M')
        ])
        
    output = si.getvalue()
    si.close()
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=budget_event_{event.id}.csv"}
    )
