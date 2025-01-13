#!/usr/bin/python3
"""
This module contains the routes for adding a new product to the catalog
"""

from flask import Blueprint, render_template, request, redirect, url_for
from shophive_packages.models.product import Product
from shophive_packages import db

new_product_bp = Blueprint("new_product", __name__)


@new_product_bp.route("/add-product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        new_product = Product(
            name=request.form["name"],
            description=request.form["description"],
            price=float(request.form["price"]),
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for("home_bp.home"))
    return render_template("add_product.html")
