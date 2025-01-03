#!/usr/bin/python3
"""
This module contains the routes for deleting a product from the catalog
"""
from flask import Blueprint, jsonify
from shophive_packages.models.product import Product
from shophive_packages import db

delete_product_bp = Blueprint('delete_product', __name__)


@delete_product_bp.route(
    "/api/products/<int:product_id>", methods=['DELETE'], strict_slashes=False)
def delete_product(product_id):
    """
    Api endpoint to delete a product from the catalog by ID
    """
    # get the product id
    product = Product.query.get(product_id)

    # Handle product missing edge case
    if not product:
        return jsonify({
            "message": f"Product with ID {product_id} not found"}), 404

    # delete the product and commit
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify(
            {"message": f"Product with ID {product_id} deleted"}), 200
    # Handle any errors by rolling back transaction
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting product: {str(e)}"}), 500
