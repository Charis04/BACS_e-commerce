from flask import Blueprint, render_template
from shophive_packages.models.product import Product

home_bp = Blueprint("home_bp", __name__)


@home_bp.route("/", methods=["GET"], strict_slashes=False)
@home_bp.route("/home", methods=["GET"], strict_slashes=False)
def home():
    products = Product.query.all()
    return render_template("home.html", products=products)
