from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(role):
    """
    A decorator to restrict access to routes based on user roles.
    :param role: Required role for accessing the route.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            if current_user.role != role:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def admin_required(fn):
    """
    A decorator to restrict access to admin-only routes.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'admin':
            flash('This page is restricted to administrators.', 'error')
            return redirect(url_for('auth.login'))
        
        return fn(*args, **kwargs)
    return wrapper