from functools import wraps
from flask import session, redirect, url_for, flash

def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if session.get('role') != role:
                flash("Unauthorized access", "danger")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

def admin_required(f):
    return role_required('admin')(f)