from flask import (
    Blueprint, render_template, Response, make_response
)
from shophive_packages.models.product import Product
from flask_wtf import FlaskForm  # type: ignore

home_bp = Blueprint("home_bp", __name__)


@home_bp.app_template_filter('price')
def price_filter(value: float) -> str:
    """Format price with commas and 2 decimal places"""
    return "{:,.2f}".format(float(value))


@home_bp.app_context_processor
def utility_processor() -> dict:
    """Make hasattr available in templates"""
    return {
        'hasattr': hasattr
    }


@home_bp.route("/", methods=["GET"], strict_slashes=False)
@home_bp.route("/home", methods=["GET"], strict_slashes=False)
def home() -> Response:
    """Home page route."""
    products = Product.query.all()
    form = FlaskForm()
    return make_response(
        render_template(
            "home.html",
            products=products,
            form=form
        )
    )
