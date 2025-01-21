from flask import (
    Blueprint, make_response, request, jsonify, render_template,
    session, flash, Response, url_for, redirect
)
from sqlalchemy import TypeDecorator
from werkzeug.wrappers import Response as WerkzeugResponse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import (
    login_user as flask_login_user, logout_user,
    login_required, current_user
)
from typing import Callable, TypeVar, cast, Union
from shophive_packages.services.auth_service import register_user
from shophive_packages.models.user import User, Seller
from shophive_packages import db
from shophive_packages.models.types import ModelProtocol, RelationshipList
from shophive_packages.services.auth_helpers import find_user, merge_guest_cart

# Typing aliases
RT = TypeVar('RT')
JWTDecorator = TypeDecorator[Callable[..., RT]]
jwt_required = cast(JWTDecorator, jwt_required)  # Type casting for JWT decorator

# Blueprint for user-related routes
user_bp = Blueprint("user_bp", __name__, url_prefix="/user")

# === User Registration ===
@user_bp.route("/register", methods=["GET", "POST"])
def register() -> Union[str, tuple[dict, int], Response, WerkzeugResponse]:
    """
    Register a new user.

    Returns:
        - For GET: Renders the registration form.
        - For POST: Redirects to login upon successful registration or returns an error message.
    """
    if request.method == "GET":
        return render_template("register.html")

    try:
        # Retrieve form data
        role = request.form.get("role", "buyer")  # Default role is buyer
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            return jsonify({"message": "Username, email, and password are required"}), 400

        # Register user and log them in
        register_user(username, email, password, role)
        user = find_user(username)
        if user:
            flask_login_user(user)
            merge_guest_cart(user)
            flash("Successfully registered!", "success")
        return make_response(redirect(url_for("user_bp.login")))
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


# === User Login ===
@user_bp.route("/login", methods=["GET", "POST"])
def login() -> WerkzeugResponse:
    """
    Log in an existing user.

    Returns:
        - Redirects to home if authenticated.
        - Renders the login form or processes login credentials.
    """
    if current_user.is_authenticated:
        return make_response(redirect(url_for("home_bp.home")))

    if request.method == "POST":
        session.pop("_flashes", None)
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password are required.", "error")
            return make_response(render_template("login.html"))

        user = find_user(username)
        if user and user.check_password(password):
            flask_login_user(user)
            if hasattr(user, "get_cart"):
                merge_guest_cart(user)
            flash("Logged in successfully.", "success")
            next_page = request.args.get("next")
            return make_response(redirect(next_page or url_for("home_bp.home")))

        flash("Invalid username or password.", "error")

    return make_response(render_template("login.html"))


# === View Shop (For Sellers) ===
@user_bp.route("/shop", methods=["GET"])
@jwt_required()
def view_shop() -> tuple[dict, int]:
    """
    View products for sellers.

    Returns:
        - List of products if user is a seller.
        - Access denied error if user is not a seller.
    """
    current_user_id = get_jwt_identity()
    user: User = User.query.get_or_404(current_user_id)

    if user.role != "seller":
        return jsonify({"message": "Access denied. Only sellers can view this page."}), 403

    products = [
        {"id": product.id, "name": product.name, "price": product.price}
        for product in cast(RelationshipList, user.products)
    ]
    return jsonify({"shop": products}), 200


# === View Orders (For Buyers) ===
@user_bp.route("/orders", methods=["GET"])
@jwt_required()
def view_orders() -> tuple[dict, int]:
    """
    View orders for buyers.

    Returns:
        - List of orders if user is a buyer.
        - Access denied error if user is not a buyer.
    """
    current_user_id = get_jwt_identity()
    user: User = User.query.get_or_404(current_user_id)

    if user.role != "buyer":
        return jsonify({"message": "Access denied. Only buyers can view this page."}), 403

    orders = [
        {"id": order.id, "status": order.status, "total_amount": str(order.total_amount)}
        for order in cast(RelationshipList, user.orders)
    ]
    return jsonify({"orders": orders}), 200


# === User Logout ===
@user_bp.route("/logout")
def logout() -> WerkzeugResponse:
    """
    Logs out the current user.
    """
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("user_bp.login"))


# === View User Profile ===
@user_bp.route("/profile")
@login_required
def view_profile() -> Union[str, WerkzeugResponse]:
    """
    Displays the user's profile page.
    """
    if not current_user.is_authenticated:
        flash("Please login to view your profile.", "error")
        return redirect(url_for("user_bp.login"))

    try:
        user_id = current_user.get_id()
        if not user_id:
            flash("Invalid user session.", "error")
            return redirect(url_for("user_bp.login"))

        user_type, id_str = user_id.split("_")
        user_id_int = int(id_str)
        user = db.session.query(Seller if user_type == "seller" else User).get(user_id_int)

        if not user:
            flash("User not found.", "error")
            logout_user()
            return redirect(url_for("user_bp.login"))

        return render_template("profile.html", user=user)
    except Exception as e:
        flash("Error loading profile.", "error")
        return redirect(url_for("user_bp.login"))


# === Update User Profile ===
@user_bp.route("/profile/update", methods=["POST"])
@login_required
def update_profile() -> WerkzeugResponse:
    """
    Handles profile updates.
    """
    username = request.form.get("username")
    email = request.form.get("email")
    new_password = request.form.get("new_password")

    if username and email:
        model_class = type(current_user)
        existing_user = model_class.query.filter(
            (model_class.username == username) & (model_class.id != current_user.id)
        ).first()
        if existing_user:
            flash("Username already taken.", "error")
            return redirect(url_for("user_bp.view_profile"))

        existing_email = model_class.query.filter(
            (model_class.email == email) & (model_class.id != current_user.id)
        ).first()
        if existing_email:
            flash("Email already registered.", "error")
            return redirect(url_for("user_bp.view_profile"))

        current_user.username = username
        current_user.email = email

        if new_password:
            current_user.set_password(new_password)

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except Exception:
            db.session.rollback()
            flash("An error occurred while updating your profile.", "error")

    return redirect(url_for("user_bp.view_profile"))
