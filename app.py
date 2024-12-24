import os
from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_restful import Api
from shophive_packages import db

# Initialize Flask application
app: Flask = Flask(__name__, template_folder="shophive_packages/templates")

# Configure SQLAlchemy database URI and settings
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
    from shophive_packages.models import User, Product

    print(f"Registered tables: {db.metadata.tables.keys()}")

# Initialize Flask-RESTful API
api: Api = Api(app)

# Import and add your cart routes here
from shophive_packages.routes.cart_routes import CartResource

api.add_resource(CartResource, "/cart", "/cart/<int:cart_item_id>")


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


@app.route("/add-product", methods=["POST"], strict_slashes=False)
def add_product() -> tuple:
    """
    Add a new product to the database.

    Returns:
        tuple: A success message and the HTTP status code.
    """
    from shophive_packages.models import Product

    data = request.json
    new_product = Product(
        name=data["name"], description=data["description"], price=data["price"]
    )
    db.session.add(new_product)
    db.session.commit()
    return {"message": "Product added successfully!"}, 201


@app.route("/delete-product/<int:product_id>", methods=["DELETE"], strict_slashes=False)
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


if __name__ == "__main__":
    """
    Run the Flask application.

    The app will run in debug mode on the default Flask port (5000).
    """
    app.run(debug=True)
