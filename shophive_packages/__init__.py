from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # type: ignore
from flask_jwt_extended import JWTManager
from flask_login import LoginManager  # type: ignore
from flask_restful import Api  # type: ignore # noqa
from flask_session import Session  # type: ignore
from flask_wtf.csrf import CSRFProtect  # type: ignore
import os
from dotenv import load_dotenv
from datetime import timedelta
from typing import TYPE_CHECKING

from config import config

if TYPE_CHECKING:
    from shophive_packages.models.user import User

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
login_manager = LoginManager()
flask_session = Session()
csrf = CSRFProtect()


def format_price(value: float | str) -> str:
    """Custom filter to format price with commas and 2 decimal places"""
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return "0.00"


def create_app(config_name: str = "default") -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config_name (str): The configuration name to use.

    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config[config_name])

    # Initialize app config
    config[config_name].init_app(app)

    # Important: Set secret key first
    app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Make sure this is set

    # Disable CSRF protection
    app.config['WTF_CSRF_ENABLED'] = False

    # Configure session handling
    session_dir = os.path.join(os.getcwd(), "flask_session")
    os.makedirs(session_dir, exist_ok=True)  # Ensure directory exists

    app.config.update(
        SESSION_TYPE="filesystem",
        SESSION_FILE_DIR=session_dir,
        SESSION_KEY_PREFIX="shophive:",
        SESSION_FILE_THRESHOLD=500,
        SESSION_FILE_MODE=0o600,
        SESSION_COOKIE_NAME="shophive_session",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,  # Set to True in production
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_PERMANENT=True,
        PERMANENT_SESSION_LIFETIME=timedelta(days=31),
        SESSION_REFRESH_EACH_REQUEST=True,
    )

    # Initialize Flask-Session first
    flask_session.init_app(app)

    # Initialize other extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register the custom filter
    app.jinja_env.filters['price'] = format_price

    # Configure LoginManager
    login_manager.login_view = "user_bp.login"

    @login_manager.user_loader  # type: ignore[misc]
    def load_user(user_id: int) -> "User | None":
        """
        Load a user from the database by user ID.
        """
        from shophive_packages.models.user import User

        result = User.query.get(int(user_id))
        return result if isinstance(result, User) else None

    # Register blueprints
    from shophive_packages.routes.user_api_routes import user_api_bp
    from shophive_packages.routes.auth_routes import auth_bp
    from shophive_packages.routes.order_routes import order_bp
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
    app.register_blueprint(new_product_bp)
    app.register_blueprint(update_product_bp)
    app.register_blueprint(delete_product_bp)
    app.register_blueprint(read_product_bp)
    app.register_blueprint(pagination_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_api_bp)

    return app
