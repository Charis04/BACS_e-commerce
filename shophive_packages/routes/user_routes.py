from flask import Blueprint, request, jsonify, render_template, url_for, redirect
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

    try:
        role = request.form.get("role", "buyer")  # Default role is "buyer"
        user = register_user(
            request.form.get('username'), request.form.get("email"),
            request.form.get("password"), role)
        return redirect(url_for('user_bp.login'))
        #return jsonify({"message": f"User {user.username} created successfully as a {role}!"}), 201
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

    username = request.form.get('username')
    password = request.form.get("password")
    try:
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            raise ValueError("Invalid credentials")
        token = login_user(username, password)
        return redirect(url_for('home'))
        #return jsonify({"access_token": token, "role": user.role}), 200
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
