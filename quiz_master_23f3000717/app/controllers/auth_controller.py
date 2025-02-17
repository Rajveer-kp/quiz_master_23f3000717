from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app.models.user import User
from app import db
from datetime import datetime   

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def choose_login():
    """Show the login selection page (Admin/User)"""
    return render_template('auth/choose_login.html')

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin Login Page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        admin = User.query.filter_by(email=email, role='admin').first()
        
        if admin and admin.check_password(password):
            session['user_id'] = admin.id  
            session['username'] = admin.username  
            session['role'] = 'admin'  
            return redirect(url_for('admin.dashboard'))

        flash('Invalid admin credentials', 'danger')

    return render_template('auth/admin_login.html')

@auth_bp.route('/user_login', methods=['GET', 'POST'])
def user_login():
    """User Login Route."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.user_login'))

        if user.is_blocked:
            flash('Your account has been blocked by the admin.', 'danger')
            return redirect(url_for('auth.user_login'))  # Prevent login for blocked users

        session['user_id'] = user.id  
        session['username'] = user.username  
        session['role'] = user.role  

        return redirect(url_for('user.dashboard'))

    return render_template('auth/user_login.html')



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User Registration Route."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Ensure unique email
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for('auth.register'))

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('auth.user_login'))  # Redirect to User Login

    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """Logs the user out and clears the session."""
    session.clear()  # ✅ Clears all session data
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.user_login'))  # ✅ Redirects to the correct login page
