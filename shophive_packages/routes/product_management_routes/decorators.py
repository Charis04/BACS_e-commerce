#!/usr/bin/python3
"""
This module contains decorators for checking user roles
"""

from functools import wraps
from flask import jsonify
from flask_login import current_user, login_required


def role_required(role):
    """
    Decorator to check if the current user has the specified role.
    """
    def decorator(func):
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role != role:
                return jsonify({
                    "message": "Unauthorized user! Access denied.",
                    "required_role": role,
                    "user_role": current_user.role
                    }), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator
