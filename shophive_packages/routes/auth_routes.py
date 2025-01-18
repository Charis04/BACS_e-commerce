from flask import Blueprint, jsonify, request
from shophive_packages.services.auth_service import register_user
from flask_login import (  # type: ignore
    login_user as flask_login_user,
    logout_user,
    login_required
)
from shophive_packages.models.user import User

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/register", methods=["POST"])
def register() -> tuple:
    """Handle user registration"""
    data = request.get_json()
    try:
        _ = register_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            role="buyer"
        )
        return jsonify({"message": "User registered successfully!"}), 201
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.route("/login", methods=["POST"])
def login() -> tuple:
    """Handle user login"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        user = User.query.filter_by(username=data.get("username")).first()

        if (user and "password" in data
                and user.check_password(data["password"])):
            flask_login_user(user)
            return jsonify({"message": "Logged in successfully!"}), 200
        return jsonify({"message": "Invalid credentials!"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/logout")
@login_required  # type: ignore[misc]
def logout() -> tuple:
    """Handle user logout"""
    logout_user()
    return jsonify({"message": "Logged out successfully!"}), 200
