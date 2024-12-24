import os
from typing import Tuple
from flask import Flask, render_template, request
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user,
)
from flask_migrate import Migrate
from flask_restful import Api
from shophive_packages import db
from shophive_packages.routes.cart_routes import CartResource

# Initialize Flask application
app: Flask = Flask(__name__, template_folder="shophive_packages/templates")
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Configure SQLAlchemy database URI and settings

# Uncomment the lines below for testing with an in-memory database
# app.config["TESTING"] = True
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

# Uncomment the line below for local development with a local database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY"
)  # Added secret key for session management

# Initialize the database and migration objects with the app
db.init_app(app)
migrate = Migrate(app, db)

# Debug: Print registered tables to ensure models are loaded correctly
with app.app_context():
    from shophive_packages.models import Product, User, Cart

    print(f"Registered tables: {db.metadata.tables.keys()}")

# Initialize Flask-RESTful API
api: Api = Api(app)

api.add_resource(CartResource, "/cart", "/cart/<int:cart_item_id>")


# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id: int):
    """
    Load a user from the database by user ID.

    Args:
        user_id (int): The ID of the user to load.

    Returns:
        User: The user object if found, otherwise None.
    """
    return User.query.get(int(user_id))


@app.route("/add-user/<username>/<email>", strict_slashes=False)
def add_user(username: str, email: str) -> str:
    """
    Add a new user to the database.

    Args:
        username (str): The username of the new user.
        email (str): The email of the new user.

    Returns:
        str: Success message.
    """
    from shophive_packages.models import User

    new_user = User(username=username, email=email, password="securepassword")
    db.session.add(new_user)
    db.session.commit()
    return f"User {username} added!"


@app.route("/get-users", strict_slashes=False)
def get_users() -> dict:
    """
    Retrieve all users from the database.

    Returns:
        dict: A dictionary of user IDs and usernames.
    """
    users = User.query.all()
    return {user.id: user.username for user in users}


@app.route("/", strict_slashes=False)
def home() -> str:
    """
    Render the homepage with a list of products.

    Returns:
        HTML: Rendered homepage.
    """
    products = Product.query.all()
    return render_template("home.html", products=products)


@app.route("/add-product", methods=["POST"], strict_slashes=False)
def add_product() -> tuple:
    """
    Add a new product to the database.

    Returns:
        tuple: A success message and the HTTP status code.
    """
    data = request.json
    new_product = Product(
        name=data["name"], description=data["description"], price=data["price"]
    )
    db.session.add(new_product)
    db.session.commit()
    return {"message": "Product added successfully!"}, 201


@app.route("/delete-product/<int:product_id>", methods=["DELETE"],
           strict_slashes=False)
def delete_product(product_id: int) -> tuple:
    """
    Delete a product from the database.

    Args:
        product_id (int): The ID of the product to delete.

    Returns:
        tuple: A success or error message and the HTTP status code.
    """
    product = Product.query.get(product_id)
    if not product:
        return {"message": "Product not found!"}, 404
    db.session.delete(product)
    db.session.commit()
    return {"message": "Product deleted!"}, 200


@app.route("/register", methods=["POST"], strict_slashes=False)
def register() -> tuple:
    """
    Register a new user.

    Returns:
        tuple: A success message and the HTTP status code.
    """
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
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    if (
        user and user.password == data["password"]
    ):  # Add bcrypt for password checking later
        login_user(user)
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


@app.route("/add-to-cart/<int:product_id>", strict_slashes=False)
@login_required
def add_to_cart(product_id: int) -> Tuple[dict, int]:
    """
    Add a product to the user's cart.

    Args:
        product_id (int): The ID of the product to add to the cart.

    Returns:
        tuple: A success message and the HTTP status code, or an error message
        if the product is not found.
    """
    product = Product.query.get(product_id)
    if not product:
        return {"message": "Product not found!"}, 404
    new_cart_item = Cart(user_id=current_user.id, product_id=product.id)
    db.session.add(new_cart_item)
    db.session.commit()
    return {"message": "Product added to cart!"}, 201


if __name__ == "__main__":
    """
    Run the Flask application.

    The app will run in debug mode on the default Flask port (5000).
    """
    app.run(debug=True)
