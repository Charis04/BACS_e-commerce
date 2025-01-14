from flask import Blueprint, make_response, request, jsonify, render_template, session, flash, Response  # noqa
from flask import url_for, redirect
from sqlalchemy import TypeDecorator
from werkzeug.wrappers import Response as WerkzeugResponse
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Callable, TypeVar, cast
from flask_login import (  # type: ignore
    login_user as flask_login_user, logout_user)
from shophive_packages.services.auth_service import register_user, login_user  # noqa
from shophive_packages.models.user import User

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
        register_user(
            request.form.get("username"),
            request.form.get("email"),
            request.form.get("password"),
            role,
        )
        return make_response(redirect(url_for("user_bp.login")))
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


# User Login
@user_bp.route("/login", methods=["GET", "POST"])
def login() -> (
    str | tuple[dict, int] | Response | WerkzeugResponse | tuple[Response, int]
):
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

    if user and user.check_password(password):
        flask_login_user(user)
        return redirect(url_for("home_bp.home"))

    return jsonify({"message": "Invalid credentials"}), 401


# View Profile (Buyer or Seller)
@user_bp.route("/profile", methods=["GET"])
@jwt_required()  # type: ignore[misc]
def profile() -> tuple[dict, int] | tuple[str, int] | tuple[Response, int]:
    """
    View the profile of the logged-in user.
    Buyers can view their orders, while sellers can view their shop.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)

    if user.role == "buyer":
        orders = [
            {"id": order.id, "status": order.status}
            for order in user.orders
        ]
        return jsonify({
            "username": user.username,
            "email": user.email,
            "orders": orders
        }), 200

    elif user.role == "seller":
        products = [
            {"id": product.id, "name": product.name}
            for product in user.products
        ]
        return jsonify({
            "username": user.username,
            "email": user.email,
            "shop": products
        }), 200

    return jsonify({"message": "Invalid role"}), 400


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
