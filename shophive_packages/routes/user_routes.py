from flask import Blueprint, request, jsonify, render_template, session
from flask import url_for, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import login_user as flask_login_user
from shophive_packages.models.product import Product
from shophive_packages.services.auth_service import register_user, login_user
from shophive_packages.models.user import User

user_bp = Blueprint("user_bp", __name__, url_prefix="/user")


# User Registration
@user_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user.

    Returns:
        For GET: Render the registration form.
        For POST: Redirect to login page upon successful registration or
        return an error.
    """
    if request.method == "GET":
        return render_template("register.html")

    try:
        role = request.form.get("role", "buyer")  # Default role is "buyer"
        register_user(
            request.form.get("username"),
            request.form.get("email"),
            request.form.get("password"),
            role,
        )
        return redirect(url_for("user_bp.login"))
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


# User Login
@user_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Log in a user.

    Returns:
        For GET: Render the login form.
        For POST: Redirect to home page upon successful login or
        return an error.
    """
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    # Try finding user by username or email
    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()

    print(f"Login attempt for user: {username}")
    if user and user.check_password(password):
        flask_login_user(user)
        print(f"Success! Password verified for user: {username}")
        return redirect(url_for("home_bp.home"))

    print(f"Failed! Invalid credentials for user: {username}")
    return jsonify({"message": "Invalid credentials"}), 401


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
    return jsonify({
        "username": user.username,
        "email": user.email,
        "role": user.role
    })
