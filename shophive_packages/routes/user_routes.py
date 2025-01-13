from flask import Blueprint, request, jsonify, render_template, url_for, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from shophive_packages.services.auth_service import register_user, login_user
from shophive_packages.models import User, Product, Order

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


 View Profile (Buyer or Seller)
@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    """
    View the profile of the logged-in user.
    Buyers can view their orders, while sellers can view their shop.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)

    if user.role == "buyer":
        orders = [{"id": order.id, "status": order.status} for order in user.orders]
        return jsonify({"username": user.username, "email": user.email, "orders": orders})
    
    elif user.role == "seller":
        products = [{"id": product.id, "name": product.name} for product in user.products]
        return jsonify({"username": user.username, "email": user.email, "shop": products})

    return jsonify({"message": "Invalid role"}), 400


# View Shop (for sellers)
@user_bp.route("/shop", methods=["GET"])
@jwt_required()
def view_shop():
    """
    Allows sellers to view and manage their products.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)

    if user.role != "seller":
        return jsonify({"message": "Access denied. Only sellers can view this page."}), 403

    products = [{"id": product.id, "name": product.name, "price": product.price} for product in user.products]
    return jsonify({"shop": products})


# View Orders (for buyers)
@user_bp.route("/orders", methods=["GET"])
@jwt_required()
def view_orders():
    """
    Allows buyers to view and manage their orders.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)

    if user.role != "buyer":
        return jsonify({"message": "Access denied. Only buyers can view this page."}), 403

    orders = [{"id": order.id, "status": order.status, "total_amount": str(order.total_amount)} for order in user.orders]
    return jsonify({"orders": orders})

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
