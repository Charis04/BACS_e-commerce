from flask import render_template, request
from flask_login import login_required, logout_user
from shophive_packages import db, app
from shophive_packages.services.auth_service import login_user


@app.route("/", strict_slashes=False)
def home() -> str:
    """
    Render the homepage with a list of products.

    Returns:
        HTML: Rendered homepage.
    """
    from shophive_packages.models import Product

    products = Product.query.all()
    return render_template("home.html", products=products)


@app.route("/register", methods=["POST"], strict_slashes=False)
def register() -> tuple:
    """
    Register a new user.

    Returns:
        tuple: A success message and the HTTP status code.
    """
    from shophive_packages.models import User

    data = request.json
    new_user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"],
    )
    db.session.add(new_user)
    db.session.commit()
    return {"message": "User registered successfully!"}, 201


@app.route("/login", methods=["POST"], strict_slashes=False)
def login() -> tuple:
    """
    Log in an existing user.

    Returns:
        tuple: A success message and the HTTP status code, or an error message
        if credentials are invalid.
    """
    from shophive_packages.models import User

    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    if (
        user and user.password == data["password"]
    ):  # Add bcrypt for password checking later
        login_user(user, data["password"])
        return {"message": "Logged in successfully!"}, 200
    return {"message": "Invalid credentials!"}, 401


@app.route("/logout", strict_slashes=False)
@login_required
def logout() -> tuple:
    """
    Log out the current user.

    Returns:
        tuple: A success message and the HTTP status code.
    """
    logout_user()
    return {"message": "Logged out successfully!"}, 200
