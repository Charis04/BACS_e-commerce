from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from typing import Tuple
from flask_restful import Api
from config import config
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user,
)


# load environment variables
load_dotenv()


def create_app(config_name="default"):
    """
    Create and configure the Flask application.

    Args:
        config_name (str): The configuration name to use.


for rule in app.url_map.iter_rules():
    print(f"{rule} -> {rule.methods}")


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5003, debug=True)
    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(__name__, template_folder="shophive_packages/templates")
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
#app = create_app()


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'daskjfladjsfljadsfj' #os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = 'aklsdfjladjfjasdfj' #os.getenv('SECRET_KEY')  # Add JWT_SECRET_KEY

db = SQLAlchemy(app)
# db.init_app(app)
jwt = JWTManager(app)
#migrate = Migrate(app, db)

# Register routes
from shophive_packages.routes import user_routes, order_routes, home, add_product
from shophive_packages.routes.user_routes import user_bp
from shophive_packages.routes.cart_routes import CartResource
from shophive_packages.routes.product_management_routes.new_product_routes import new_product_bp
from shophive_packages.routes.product_management_routes.update_product_routes import update_product_bp
from shophive_packages.routes.product_management_routes.delete_product_routes import delete_product_bp
from shophive_packages.routes.product_management_routes.read_product_routes import read_product_bp
from shophive_packages.routes.product_management_routes.pagination_routes import pagination_bp

app.register_blueprint(new_product_bp)
app.register_blueprint(update_product_bp)
app.register_blueprint(delete_product_bp)
app.register_blueprint(pagination_bp)
app.register_blueprint(read_product_bp)
app.register_blueprint(user_bp)
