import os
from typing import Tuple
from flask import Flask, redirect, render_template, request, url_for
from flask_jwt_extended import JWTManager
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
from shophive_packages.routes.user_routes import user_bp
from config import config


def create_app(config_name="default"):
    """
    Create and configure the Flask application.

    Args:
        config_name (str): The configuration name to use.

    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(
        __name__,
        template_folder="shophive_packages/templates",
        static_folder="shophive_packages/static",
    )
    app.config.from_object(config[config_name])

    # Configure SQLAlchemy database URI and settings
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY"
    )  # Add secret key for session management
    app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Uncomment the lines below for testing with an in-memory database
    # app.config["TESTING"] = True
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    # Uncomment the line below for local development with a local database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

    # Initialize the database and migration objects with the app
    db.init_app(app)
    jwt = JWTManager(app)  # noqa
    migrate = Migrate(app, db)  # noqa

    # Debug: Print registered tables to ensure models are loaded correctly
    with app.app_context():
        from shophive_packages.models import Product, User, Cart  # noqa

        print(f"Registered tables: {db.metadata.tables.keys()}")

    # Initialize Flask-Login
    login_manager = LoginManager(app)
    login_manager.login_view = "login"

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

    # Initialize Flask-RESTful API
    api = Api(app)
    api.add_resource(CartResource, "/cart", "/cart/<int:cart_item_id>")

    # Register blueprints
    app.register_blueprint(user_bp, url_prefix="/")

    return app


# Create the app
app = create_app()


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
    from shophive_packages.models import User

    users = User.query.all()
    return {user.id: user.username for user in users}


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


@app.route("/add-product", methods=["GET", "POST"], strict_slashes=False)
def add_product() -> tuple:
    """
    Add a new product to the database.

    Handles both JSON-based API requests and form submissions.

    Returns:
        - On success (JSON): A success message and the HTTP status code.
        - On success (Form): Redirect to the home page or render the form with
        feedback.
    """
    from shophive_packages.models import Product

    if request.method == "POST":
        # Handle JSON request (e.g., API call)
        if request.is_json:
            data = request.get_json()
            new_product = Product(
                name=data["name"],
                description=data["description"],
                price=data["price"]
            )
            db.session.add(new_product)
            db.session.commit()
            return {"message": "Product added successfully!"}, 201

        # Handle Form submission
        else:
            name = request.form.get("name")
            description = request.form.get("description")
            price = request.form.get("price")

            if not name or not description or not price:
                return render_template(
                    "add_product.html", error="All fields are required!"
                )

            try:
                price = float(price)
                new_product = Product(name=name, description=description,
                                      price=price)
                db.session.add(new_product)
                db.session.commit()
                return redirect(url_for("home"))
            except ValueError:
                return render_template(
                    "add_product.html", error="Invalid price entered!"
                )

    # Render the form for GET request
    return render_template("add_product.html")


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
    from shophive_packages.models import Product

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
    from shophive_packages.models import Cart, Product

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
