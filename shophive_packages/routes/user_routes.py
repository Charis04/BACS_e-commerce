from flask import Blueprint, make_response, request, jsonify, render_template, session, flash, Response  # noqa
from flask import url_for, redirect
from sqlalchemy import TypeDecorator
from werkzeug.wrappers import Response as WerkzeugResponse
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Callable, TypeVar, cast
from flask_login import (  # type: ignore
    login_user as flask_login_user, logout_user, login_required, current_user)
from shophive_packages.services.auth_service import register_user, login_user  # noqa
from shophive_packages.models.user import User
from shophive_packages.models.product import Product
from shophive_packages import db

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
        return make_response(redirect(url_for("user_bp.login")))
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


# User Login
@user_bp.route("/login", methods=["GET", "POST"])
def login() -> str | WerkzeugResponse:
    """
    Log in a user.

    Returns:
        For GET: Render the login form.
        For POST: Redirect to home page upon successful login or
        return to login page with error message.
    """
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    # Try finding user by username or email
    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()

    if user and user.check_password(password):
        flask_login_user(user)

        # Merge guest cart with user cart
        guest_cart = session.get('cart_items', [])
        if guest_cart:
            for item in guest_cart:
                product = Product.query.get(item['product_id'])
                if product:
                    user.add_to_cart(product, item['quantity'])
            # Clear guest cart
            session.pop('cart_items', None)
            session.pop('cart_total', None)

        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for("home_bp.home"))

    flash('Invalid username or password', 'error')
    return redirect(url_for('user_bp.login'))


# Remove the JWT profile route since we're using Flask-Login
# Remove the entire @user_bp.route("/profile", methods=["GET"]) function


# View Shop (for sellers)
@user_bp.route("/shop", methods=["GET"])
@jwt_required()  # type: ignore[misc]
def view_shop() -> tuple[Response | dict, int]:
    """
    Allows sellers to view and manage their products.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)

    if user.role != "seller":
        return jsonify(
            {"message": "Access denied. Only sellers can view this page."}
        ), 403

    products = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
        for product in user.products
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
    user = User.query.get_or_404(current_user_id)

    if user.role != "buyer":
        return jsonify(
            {"message": "Access denied. Only buyers can view this page."}
        ), 403

    orders = [
        {
            "id": order.id,
            "status": order.status,
            "total_amount": str(order.total_amount)
        }
        for order in user.orders
    ]
    return jsonify({"orders": orders}), 200


@user_bp.route('/logout')
def logout() -> WerkzeugResponse:
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('user_bp.login'))


@user_bp.route('/profile')  # Changed from '/profile/view'
@login_required  # type: ignore
def view_profile() -> str:
    """Display user profile page"""
    return render_template('profile.html')


@user_bp.route('/profile/update', methods=['POST'])
@login_required  # type: ignore
def update_profile() -> WerkzeugResponse:
    """Handle profile updates"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        new_password = request.form.get('new_password')

        if username and email:
            # Check if username is already taken by another user
            existing_user = User.query.filter(
                User.username == username,
                User.id != current_user.id
            ).first()
            if existing_user:
                flash('Username already taken.', 'error')
                return redirect(url_for('user_bp.profile'))

            # Check if email is already taken by another user
            existing_email = User.query.filter(
                User.email == email,
                User.id != current_user.id
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
