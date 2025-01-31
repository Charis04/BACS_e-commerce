from flask import (
    Blueprint, request, render_template, redirect, url_for, Response
)
from werkzeug.wrappers import Response as WerkzeugResponse
from shophive_packages import db
from typing import Union
from typing_extensions import TypeAlias

ResponseReturnValue: TypeAlias = Union[
    str, tuple, dict, Response, WerkzeugResponse
]

# Update the blueprint name to match what's used in the template
add_product_bp = Blueprint('add_product_bp', __name__)


@add_product_bp.route("/add-product", methods=["GET", "POST"])
def add_product() -> ResponseReturnValue:
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
                ), 400

            try:
                price_float = float(price)
                new_product = Product(name=name, description=description,
                                      price=price_float)
                db.session.add(new_product)
                db.session.commit()
                return redirect(url_for("home_bp.home"))
            except ValueError:
                return render_template(
                    "add_product.html", error="Invalid price entered!"
                ), 400

    # Render the form for GET request
    return render_template("add_product.html"), 200
