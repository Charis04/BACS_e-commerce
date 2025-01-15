#!/usr/bin/python3
"""
This module contains the routes for deleting a product from the catalog
"""
from flask import Blueprint, jsonify, Response, redirect, url_for, flash
import werkzeug.wrappers
from shophive_packages.models.product import Product
from shophive_packages import db
from shophive_packages.db_utils import get_by_id

delete_product_bp = Blueprint('delete_product', __name__)


@delete_product_bp.route(
    "/api/products/<int:product_id>", methods=['DELETE'], strict_slashes=False)
def delete_product(product_id: int) -> tuple[Response, int]:
    """
    Api endpoint to delete a product from the catalog by ID
    """
    # get the product id
    product = get_by_id(Product, product_id)

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


@delete_product_bp.route("/delete-product/<int:product_id>", methods=["POST"])
def delete_product_ui(
        product_id: int) -> tuple[werkzeug.wrappers.Response, int]:
    """Delete a product from the UI"""
    try:
        product = get_by_id(Product, product_id)
        if not product:
            flash('Product not found!', 'error')
            return redirect(url_for('home_bp.home')), 404
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
        return redirect(url_for('home_bp.home')), 302
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'error')
        return redirect(url_for('home_bp.home')), 302
