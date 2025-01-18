from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # type: ignore
from flask_jwt_extended import JWTManager
from flask_login import LoginManager  # type: ignore
from flask_restful import Api  # type: ignore # noqa
from flask_session import Session  # type: ignore
from flask_wtf.csrf import CSRFProtect  # type: ignore
from flask_login import current_user
import os
from dotenv import load_dotenv
from datetime import timedelta
from typing import TYPE_CHECKING, Optional, Union

from config import config

if TYPE_CHECKING:
    from shophive_packages.models.user import User, Seller

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


def setup_config(app: Flask, config_name: str) -> None:
    """Configure application settings."""
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['WTF_CSRF_ENABLED'] = False


def setup_session(app: Flask) -> None:
    """Configure session handling."""
    session_dir = os.path.join(os.getcwd(), "flask_session")
    os.makedirs(session_dir, exist_ok=True)

    app.config.update(
        SESSION_TYPE="filesystem",
        SESSION_FILE_DIR=session_dir,
        SESSION_PERMANENT=True,
        PERMANENT_SESSION_LIFETIME=timedelta(days=31),
        SESSION_REFRESH_EACH_REQUEST=True,
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )


def init_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    flask_session.init_app(app)

    app.jinja_env.filters['price'] = format_price

    # Configure LoginManager
    login_manager.login_view = "user_bp.login"
    login_manager.session_protection = "strong"
    login_manager.login_message_category = "info"


def register_blueprints(app: Flask) -> None:
    """Register all blueprints."""
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

    blueprints = [
        home_bp,
        npr.new_product_bp,
        upr.update_product_bp,
        dpr.delete_product_bp,
        rpr.read_product_bp,
        pr.pagination_bp,
        user_bp,
        cart_bp,
        checkout_bp,
        order_bp,
        auth_bp,
        user_api_bp,
    ]

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def create_app(config_name: str = "default") -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="templates")

    setup_config(app, config_name)
    setup_session(app)

    with app.app_context():
        init_extensions(app)

    register_blueprints(app)

    @app.context_processor
    def inject_cart_count() -> dict:
        """Inject cart count into all templates."""
        from shophive_packages.models.cart import Cart
        from flask import session

        cart_count = 0
        app.logger.debug("Starting cart count calculation")

        if current_user and current_user.is_authenticated:
            try:
                # Extract numeric ID from user_id string (e.g., "user_2" -> 2)
                if (isinstance(current_user.id, str) and
                        '_' in current_user.id):
                    user_id = int(current_user.id.split('_')[1])
                else:
                    user_id = int(current_user.id)

                app.logger.debug(f"User ID (parsed): {user_id}")
                cart_items = Cart.query.filter_by(user_id=user_id).all()
                cart_count = (sum(item.quantity for item in cart_items)
                              if cart_items else 0)
                app.logger.debug(
                    f"Authenticated user cart count: {cart_count}")
            except Exception as e:
                app.logger.error(
                    "Error calculating authenticated cart count: "
                    f"{str(e)}"
                )
                cart_count = 0
        else:
            # Handle anonymous users with session cart
            try:
                cart_items = session.get('cart_items', [])
                cart_count = sum(
                    item.get('quantity', 0) for item in cart_items
                )
                app.logger.debug(f"Anonymous user cart count: {cart_count}")
            except Exception as e:
                app.logger.error(
                    f"Error calculating anonymous cart count: {str(e)}")
                cart_count = 0

        app.logger.debug(f"Final cart count: {cart_count}")
        return {'cart_count': cart_count}

    return app


@login_manager.user_loader  # type: ignore[misc]
def load_user(user_id: str) -> Optional[Union["User", "Seller"]]:
    """Load user by ID."""
    from shophive_packages.models.user import User, Seller

    try:
        if '_' not in user_id:
            return None

        user_type, id_str = user_id.split('_')
        user_id_int = int(id_str)

        # Query base User table first to determine type
        base_user = User.query.get(user_id_int)
        if not base_user:
            return None

        # Return appropriate type based on user_type
        if user_type == 'seller' and isinstance(base_user, Seller):
            return base_user
        elif user_type == 'user' and type(base_user) is User:
            return base_user
        return None

    except (ValueError, AttributeError):
        return None
