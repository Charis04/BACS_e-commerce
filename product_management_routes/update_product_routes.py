#!/usr/bin/python3
"""
This module contains the routes for updating a product in the catalog
"""
from flask import Blueprint, jsonify, request
from shophive_packages.models.product import Product
from shophive_packages import db

update_product_bp = Blueprint('update_product', __name__)


@update_product_bp.route(
    "/api/products/<int:product_id>", methods=['PUT'], strict_slashes=False)
def update_product(product_id):
    """
    Api endpoint to update a product in the catalog
    Accepts the updated product details via JSON payload
    Args:
        product_id - generated id of the product being updated
    """
    # get the product id
    product = Product.query.get(product_id)

    # Handle product missing edge case
    if not product:
        return jsonify(
            {"message": f"Product with ID {product_id} not found"}), 404

    # parse the JSON payload
    data = request.get_json()

    if not data:
        return jsonify({"message": "No input data provided"}), 400

    # validation and updating
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')

    if name:
        product.name = name
    if description:
        product.description = description
    if price:
        # check for non positive integers as prices
        if not isinstance(price, (int, float)) or price <= 0:
            return jsonify({"message": "Price must be a positive integer"})
        # if it is a positive integer or float
        product.price = price

    # committing the changes to the database
    try:
        db.session.commit()
        return jsonify({
            "message": "Product updated successfully",
            "product": {
                "id": product.name,
                "name": product.name,
                "description": product.description,
                "price": product.price
            }
        }), 200

    except Exception as e:
        # reverse the update if there is an error
        db.session.rollback()
        return jsonify({"message": str(e)}), 500
