from flask import Blueprint, request, jsonify, current_app  # noqa
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import register_user, login_user
from shophive_packages.models import User

user_bp = Blueprint("user_bp", __name__)


# User Registration
@user_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.

    Returns:
        tuple: A success message and HTTP status code 201 if registration is
        successful, or an error message and HTTP status code 400 if
        registration fails.
    """
    data = request.get_json()
    try:
        user = register_user(data["username"], data["email"], data["password"])
        return jsonify({"message":
                        f"User {user.username} created successfully!"}), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


# User Login
@user_bp.route("/login", methods=["POST"])
def login():
    """
    Log in a user.

    Returns:
        tuple: An access token and HTTP status code 200 if login is successful,
               or an error message and HTTP status code 401 if login fails.
    """
    data = request.get_json()
    try:
        token = login_user(data["username"], data["password"])
        return jsonify({"access_token": token}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 401


# User Profile
@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    """
    Get the profile of the current user.

    Returns:
        JSON: The username and email of the current user.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    return jsonify({"username": user.username, "email": user.email})
