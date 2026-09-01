"""
EventSphere - Authentication Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from app import db
from app.models.user import User, UserRole
from app.forms.auth_forms import LoginForm, RegistrationForm
from app.models.audit_log import AuditLog

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        print(f"Login attempt for username: {form.username.data}")
        print(f"User found: {user is not None}")
        if user:
            print(f"Password check: {user.check_password(form.password.data)}")
            print(f"Is active: {user.is_active}")
        
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user, remember=form.remember_me.data)
            
            # Log login action
            AuditLog.log_action(
                user_id=user.id,
                action='login',
                entity='user',
                entity_id=user.id,
                details=f"User {user.username} logged in",
                request=request
            )
            
            # Redirect to appropriate dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            elif user.is_organizer:
                return redirect(url_for('organizer.dashboard'))
            elif user.is_attendee:
                return redirect(url_for('attendee.dashboard'))
            elif user.is_vendor:
                return redirect(url_for('vendor.dashboard'))
            
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username, password, or account is disabled.', 'error')
    
    return render_template('auth/login.html', form=form, title='Login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip(),
            password=form.password.data,
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip() if form.last_name.data else None,
            phone=form.phone.data.strip() if form.phone.data else None,
            role=form.role.data
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log registration action
        AuditLog.log_action(
            user_id=user.id,
            action='register',
            entity='user',
            entity_id=user.id,
            details=f"User {user.username} registered with role {user.role}",
            request=request
        )
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form, title='Register')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route."""
    # Log logout action
    AuditLog.log_action(
        user_id=current_user.id,
        action='logout',
        entity='user',
        entity_id=current_user.id,
        details=f"User {current_user.username} logged out",
        request=request
    )
    
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Generic user profile route."""
    if current_user.is_vendor:
        return redirect(url_for('vendor.profile'))
        
    return render_template('auth/profile.html', title='My Profile')
