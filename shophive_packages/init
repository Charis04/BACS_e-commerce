from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_restful import Api
import os
from dotenv import load_dotenv

# Import the configuration disctionary
from config import config

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
login_manager = LoginManager()


def create_app(config_name="default"):
    """
    Create and configure the Flask application.

    Args:
        config_name (str): The configuration name to use.

    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(__name__, template_folder="shophive_packages/templates")
    app.config.from_object(config[config_name])

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)

    # Configure LoginManager
    login_manager.login_view = "user.login"

    @login_manager.user_loader
    def load_user(user_id):
        """
        Load a user from the database by user ID.
        """
        from shophive_packages.models import User
        return User.query.get(int(user_id))

    # Register blueprints
    from shophive_packages.routes.user_routes import user_bp
    from shophive_packages.routes.cart_routes import CartResource
    from shophive_packages.routes.product_management_routes import (
        new_product_bp, update_product_bp, delete_product_bp, read_product_bp, pagination_bp
    )

    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(new_product_bp)
    app.register_blueprint(update_product_bp)
    app.register_blueprint(delete_product_bp)
    app.register_blueprint(read_product_bp)
    app.register_blueprint(pagination_bp)

    # Register RESTful API resources
    api = Api(app)
    api.add_resource(CartResource, "/cart", "/cart/<int:cart_item_id>")

    return app
