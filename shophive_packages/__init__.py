from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_restful import Api
import os
from dotenv import load_dotenv
from datetime import timedelta

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
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config[config_name])

    # Set secret key and session configuration
    app.secret_key = app.config["SECRET_KEY"]
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=31)
    app.config["SESSION_FILE_DIR"] = os.path.join(os.getcwd(), "flask_session")

    if not os.path.exists(app.config["SESSION_FILE_DIR"]):
        os.makedirs(app.config["SESSION_FILE_DIR"])

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)

    # Configure LoginManager
    login_manager.login_view = "user_bp.login"

    @login_manager.user_loader
    def load_user(user_id):
        """
        Load a user from the database by user ID.
        """
        from shophive_packages.models.user import User

        return User.query.get(int(user_id))

    # Register blueprints
    from shophive_packages.routes.home import home_bp
    from shophive_packages.routes.user_routes import user_bp
    from shophive_packages.routes.cart_routes import cart_bp
    from shophive_packages.routes.checkout_routes import checkout_bp
    from shophive_packages.routes.product_management_routes import (
        delete_product_routes as dpr,
        new_product_routes as npr,
        pagination_routes as pr,
        read_product_routes as rpr,
        update_product_routes as upr,
    )
    new_product_bp = npr.new_product_bp
    update_product_bp = upr.update_product_bp
    delete_product_bp = dpr.delete_product_bp
    read_product_bp = rpr.read_product_bp
    pagination_bp = pr.pagination_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(new_product_bp, url_prefix="")
    app.register_blueprint(update_product_bp)
    app.register_blueprint(delete_product_bp)
    app.register_blueprint(read_product_bp)
    app.register_blueprint(pagination_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)

    # Register RESTful API resources
    api = Api(app)
    from shophive_packages.routes.cart_routes import CartResource

    api.add_resource(CartResource, "/api/cart", "/api/cart/<int:cart_item_id>")

    return app


# Create the application instance
app = create_app()
