from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from shophive_packages.services.auth_service import register_user, login_user
from shophive_packages.models import User

user_bp = Blueprint("user_bp", __name__)


# User Registration
@user_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user.

    Returns:
        For GET: Render the registration form.
        For POST: A success message and HTTP status code 201 if registration
                  is successful, or an error message and HTTP status code 400.
    """
    if request.method == "GET":
        return render_template("register.html")

    data = request.get_json()
    try:
        role = data.get("role", "buyer")  # Default role is "buyer"
        user = register_user(data["username"], data["email"], data["password"], role=role)
        return jsonify({"message": f"User {user.username} created successfully as a {role}!"}), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


# User Login
@user_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Log in a user.

    Returns:
        For GET: Render the login form.
        For POST: An access token, user role, and HTTP status code 200 if login
                  is successful, or an error message and HTTP status code 401.
    """
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json()
    try:
        user = User.query.filter_by(username=data["username"]).first()
        if not user or not user.check_password(data["password"]):
            raise ValueError("Invalid credentials")
        token = login_user(data["username"], data["password"])
        return jsonify({"access_token": token, "role": user.role}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 401


# User Profile
@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    """
    Get the profile of the current user.

    Returns:
        JSON: The username, email, and role of the current user.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    return jsonify({"username": user.username, "email": user.email, "role": user.role})
