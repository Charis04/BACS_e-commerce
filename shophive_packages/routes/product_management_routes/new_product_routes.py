#!/usr/bin/python3
"""
This module contains the routes for adding a new product to the catalog
"""

from flask import (
    Blueprint, render_template, request, redirect, url_for
)
from typing import Union
from werkzeug.wrappers import Response as WerkzeugResponse
from shophive_packages.models.product import Product
from shophive_packages import db
from flask_login import current_user, login_required  # type: ignore

new_product_bp = Blueprint("new_product_bp", __name__)


@new_product_bp.route("/add-product", methods=["GET", "POST"])
@login_required  # type: ignore
def add_product() -> Union[str, WerkzeugResponse]:
    """Add a new product"""
    if current_user.role != 'seller':
        return redirect(url_for('home_bp.home'))

    if request.method == "POST":
        new_product = Product(
            name=request.form["name"],
            description=request.form["description"],
            price=float(request.form["price"]),
            seller_id=current_user.id  # Add this line
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for("home_bp.home"), code=302)
    return render_template("add_product.html")
