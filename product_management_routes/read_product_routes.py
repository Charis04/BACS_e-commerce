#!/usr/bin/python3
"""
This module contains the routes for reading product data
"""
from flask import Blueprint, jsonify, request
from shophive_packages.models.product import Product
from shophive_packages import db

read_product_bp = Blueprint('read_product', __name__)


@read_product_bp.route("/api/products", methods=['GET'], strict_slashes=False)
def get_all_products():
    """
    Api endpoint to get all products from the catalog
    """
    limit = request.args.get('limit', type=int, default=50)

    # Enforce a maximum limit
    MAX_LIMIT = 100
    if limit > MAX_LIMIT:
        return jsonify({"message": f"Limit cannot exceed {MAX_LIMIT}"}), 400
    if limit <= 0:
        return jsonify({"message": "Limit must be a positive integer"}), 400

    try:
        # Query all products
        products = db.session.query(Product).order_by(
            Product.created_at.desc()).limit(limit).all()

        # serialize the products
        products_list = [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "image_url": product.image_url,
                "tags": [{"id": tag.id, "name": tag.name}
                         for tag in product.tags],
                "categories": [{"id": category.id, "name": category.name}
                               for category in product.categories]
            }
            for product in products
            ]
        return jsonify({"products": products_list}), 200
    except Exception as e:
        return jsonify({"messsage": str(e)}), 500


@read_product_bp.route("/api/products/<int:product_id>",
                       methods=['GET'], strict_slashes=False)
def get_product_by_id(product_id):
    """
    Api endpoint to get a product from the catalog by ID
    """
    try:
        # Query the product by ID
        product = Product.query.get(product_id)

        # serialize the product
        product_dict = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
            "image_url": product.image_url,
            "tags": [{"id": tag.id, "name": tag.name}
                     for tag in product.tags],
            "categories": [{"id": category.id, "name": category.name}
                           for category in product.categories]

        }
        return jsonify({"product": product_dict}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
