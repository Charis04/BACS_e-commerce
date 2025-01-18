from flask import Blueprint, make_response, request, jsonify, render_template, session, flash, Response  # noqa
from flask import url_for, redirect
from sqlalchemy import TypeDecorator
from werkzeug.wrappers import Response as WerkzeugResponse
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Callable, TypeVar, cast, Union
from flask_login import (  # type: ignore
    login_user as flask_login_user,
    logout_user,
    login_required,
    current_user
)
from shophive_packages.services.auth_service import register_user, login_user as auth_service_login  # noqa
from shophive_packages.models.user import User, Seller
from shophive_packages import db
from shophive_packages.models.types import ModelProtocol
from shophive_packages.models.types import RelationshipList
from shophive_packages.services.auth_helpers import find_user, merge_guest_cart

RT = TypeVar('RT')
JWTDecorator = TypeDecorator[Callable[..., RT]]
jwt_required = cast(JWTDecorator, jwt_required)  # type: ignore

user_bp = Blueprint("user_bp", __name__, url_prefix="/user")


# User Registration
@user_bp.route("/register", methods=["GET", "POST"])
def register() -> str | tuple[dict, int] | Response | tuple[Response, int]:
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
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            return jsonify(
                {"message": "Username, email and password are required"}
            ), 400

        register_user(
            username,
            email,
            password,
            role,
        )
        user = find_user(username)
        if user is not None:
            flask_login_user(user)
            merge_guest_cart(user)
            flash('Successfully registered!', 'success')
        return make_response(redirect(url_for("user_bp.login")))
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


@user_bp.route("/register", methods=["POST"])
def register_post() -> Union[WerkzeugResponse, tuple[Response, int]]:
    try:
        username = request.form.get("username")
        email = request.form.get("email")
        # Default to buyer if not specified
        role = request.form.get("role", "buyer")
        password = request.form.get("password")

        if not username or not email or not password:
            return jsonify(
                {"message": "Username, email and password are required"}
            ), 400

        register_user(username, email, password, role)
        user = find_user(username)
        if user is None:
            return jsonify({"message": "User registration failed"}), 400
        flask_login_user(user)
        merge_guest_cart(user)
        flash('Successfully registered!', 'success')
        return make_response(redirect(url_for("user_bp.login")))
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


# User Login
@user_bp.route('/login', methods=['GET', 'POST'])
def login() -> Response:
    if current_user.is_authenticated:
        return make_response(redirect(url_for('home_bp.home')))

    if request.method == 'POST':
        session.pop('_flashes', None)
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return make_response(render_template('login.html'))

        # Use find_user helper to check both User and Seller tables
        user = find_user(username)

        if user and user.check_password(password):
            flask_login_user(user)
            if hasattr(user, 'get_cart'):
                merge_guest_cart(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return make_response(
                redirect(next_page or url_for('home_bp.home'))
            )

        flash('Invalid username or password.', 'error')

    return make_response(render_template('login.html'))


# View Shop (for sellers)
@user_bp.route("/shop", methods=["GET"])
@jwt_required()  # type: ignore[misc]
def view_shop() -> tuple[Response | dict, int]:
    """
    Allows sellers to view and manage their products.
    """
    current_user_id = get_jwt_identity()
    user: User = User.query.get_or_404(current_user_id)

    if user.role != "seller":
        return jsonify(
            {"message": "Access denied. Only sellers can view this page."}
        ), 403

    # Cast the relationship to a list
    user_products = cast(RelationshipList, user.products)

    products = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
        for product in user_products
    ]
    return jsonify({"shop": products}), 200


# View Orders (for buyers)
@user_bp.route("/orders", methods=["GET"])
@jwt_required()  # type: ignore[misc]
def view_orders() -> tuple[dict | Response, int]:
    """
    Allows buyers to view and manage their orders.
    """
    current_user_id = get_jwt_identity()
    user: User = User.query.get_or_404(current_user_id)

    if user.role != "buyer":
        return jsonify(
            {"message": "Access denied. Only buyers can view this page."}
        ), 403

    # Cast the relationship to a list
    user_orders = cast(RelationshipList, user.orders)

    orders = [
        {
            "id": order.id,
            "status": order.status,
            "total_amount": str(order.total_amount)
        }
        for order in user_orders
    ]
    return jsonify({"orders": orders}), 200


@user_bp.route('/logout')
def logout() -> WerkzeugResponse:
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('user_bp.login'))


@user_bp.route('/profile')
@login_required  # type: ignore
def view_profile() -> str | WerkzeugResponse:
    """Display user profile page"""
    if not current_user.is_authenticated:
        flash('Please login to view your profile.', 'error')
        return redirect(url_for('user_bp.login'))

    try:
        user_id = current_user.get_id()
        if not user_id:
            flash('Invalid user session', 'error')
            return redirect(url_for('user_bp.login'))

        user_type, id_str = user_id.split('_')
        user_id_int = int(id_str)

        # Query the correct table based on user type
        if user_type == 'seller':
            user = db.session.query(Seller).get(user_id_int)
        else:
            user = db.session.query(User).get(user_id_int)

        if not user:
            flash('User not found', 'error')
            logout_user()
            return redirect(url_for('user_bp.login'))

        return render_template('profile.html', user=user)

    except Exception:
        flash('Error loading profile', 'error')
        return redirect(url_for('user_bp.login'))


@user_bp.route('/profile/update', methods=['POST'])
@login_required  # type: ignore
def update_profile() -> WerkzeugResponse:
    """Handle profile updates"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        new_password = request.form.get('new_password')

        if username and email:
            # Get the correct model class based on current user type
            model_class = type(current_user)
            if not isinstance(model_class, ModelProtocol):
                model_class = User  # fallback to User model

            # Check if username is already taken by another user
            existing_user = model_class.query.filter(
                (model_class.username == username) &
                (model_class.id != current_user.id)
            ).first()
            if existing_user:
                flash('Username already taken.', 'error')
                return redirect(url_for('user_bp.profile'))

            # Check if email is already taken by another user
            existing_email = model_class.query.filter(
                (model_class.email == email) &
                (model_class.id != current_user.id)
            ).first()
            if existing_email:
                flash('Email already registered.', 'error')
                return redirect(url_for('user_bp.profile'))

            current_user.username = username
            current_user.email = email

            if new_password:
                current_user.set_password(new_password)

            try:
                db.session.commit()
                flash('Profile updated successfully!', 'success')
            except Exception:
                db.session.rollback()
                flash(
                    'An error occurred while updating your profile.',
                    'error'
                )

    return redirect(url_for('user_bp.view_profile'))
