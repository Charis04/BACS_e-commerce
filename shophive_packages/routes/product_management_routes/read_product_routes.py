#!/usr/bin/python3
"""
This module contains the routes for reading product data
"""
from flask import (
    Blueprint, jsonify, request, render_template,
    Response, make_response
)
from shophive_packages.models.product import Product
from shophive_packages import db
from shophive_packages.db_utils import get_by_id
from shophive_packages.routes.cart_routes import CartForm

read_product_bp = Blueprint("read_product", __name__)


@read_product_bp.route("/api/products", methods=["GET"], strict_slashes=False)
def get_all_products() -> tuple[Response, int]:
    """
    Api endpoint to get all products from the catalog
    """
    limit = request.args.get("limit", type=int, default=50)

    # Enforce a maximum limit
    MAX_LIMIT = 100
    if limit > MAX_LIMIT:
        return jsonify({"message": f"Limit cannot exceed {MAX_LIMIT}"}), 400
    if limit <= 0:
        return jsonify({"message": "Limit must be a positive integer"}), 400

    try:
        # Query all products
        products = (
            db.session.query(Product)
            .order_by(Product.created_at.desc())
            .limit(limit)
            .all()
        )

        # serialize the products
        products_list = [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "image_url": product.image_url,
                "tags": [
                            {"id": tag.id,
                             "name": tag.name
                             } for tag in product.tags.all()],
                "categories": [
                    {"id": category.id, "name": category.name}
                    for category in product.categories.all()
                ],
            }
            for product in products
        ]
        return jsonify({"products": products_list}), 200
    except Exception as e:
        return jsonify({"messsage": str(e)}), 500


@read_product_bp.route(
    "/api/products/<int:product_id>", methods=["GET"], strict_slashes=False
)
def get_product_by_id(product_id: int) -> tuple[Response, int]:
    """
    Api endpoint to get a product from the catalog by ID
    """
    try:
        product = get_by_id(Product, product_id)
        if not product:
            return jsonify({"message": "Product not found"}), 404

        # serialize the product
        product_dict = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
            "image_url": product.image_url,
            "tags": [
                {"id": tag.id, "name": tag.name}
                for tag in product.tags.all()
            ],
            "categories": [
                {"id": category.id, "name": category.name}
                for category in product.categories.all()
            ],
        }
        return jsonify({"product": product_dict}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@read_product_bp.route("/product/<int:product_id>")
def product_detail(product_id: int) -> Response:
    """Display product details."""
    product = Product.query.get_or_404(product_id)
    form = CartForm()  # Create form instance
    return make_response(
        render_template(
            "product_detail.html",
            product=product,
            form=form  # Pass form to template
        )
    )


@read_product_bp.route('/api/products/<int:product_id>')
def get_product_api(product_id: int) -> tuple[Response, int]:
    product = Product.query.get_or_404(product_id)
    return jsonify({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "image_url": product.image_url
    }), 200
