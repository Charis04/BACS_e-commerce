#!/usr/bin/python3
"""
This module contains the routes for updating a product in the catalog
"""
from flask import (
    Blueprint,
    jsonify,
    request,
    render_template,
    redirect,
    url_for,
    make_response
)
from werkzeug.wrappers import Response as WerkzeugResponse
from shophive_packages.models.product import Product
from shophive_packages import db
from shophive_packages.models.tags import Tag
from shophive_packages.models.categories import Category
from shophive_packages.db_utils import get_by_id


update_product_bp = Blueprint("update_product", __name__)


def _update_tags(product: Product, tags: list) -> None:
    """Helper function to update product tags"""
    product.tags.clear()
    for tag_name in tags:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        product.tags.append(tag)


def _update_categories(product: Product, categories: list) -> None:
    """Helper function to update product categories"""
    product.categories.clear()
    for category_name in categories:
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
        product.categories.append(category)


def _validate_product_data(data: dict) -> tuple:
    """Helper function to validate product data"""
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    tags = data.get("tags", [])
    categories = data.get("categories", [])
    image_url = data.get("image_url")

    if not any([name, description, price, tags, categories, image_url]):
        return jsonify({"message": "Missing required fields"}), 400

    if price and (not isinstance(price, (int, float)) or price <= 0):
        return jsonify({"message": "Price must be a positive integer"}), 400

    return None, None


def _update_product_fields(product: Product, data: dict) -> None:
    """Helper function to update product fields"""
    if data.get("name"):
        product.name = data["name"]
    if data.get("description"):
        product.description = data["description"]
    if data.get("price"):
        product.price = data["price"]
    if data.get("image_url"):
        product.image_url = data["image_url"]
    if data.get("tags"):
        _update_tags(product, data["tags"])
    if data.get("categories"):
        _update_categories(product, data["categories"])


@update_product_bp.route(
    "/api/products/<int:product_id>", methods=["PUT"], strict_slashes=False
)
def update_product_api(product_id: int) -> tuple:
    """
    Api endpoint to update a product in the catalog
    Args:
        product_id: generated id of the product being updated
    Returns:
        tuple: JSON response and status code
    """
    product = get_by_id(Product, product_id)
    if not product:
        return jsonify(
            {"message": f"Product with ID {product_id} not found"}
        ), 404

    data = request.get_json()
    validation_error = _validate_product_data(data)
    if validation_error:
        return validation_error

    try:
        _update_product_fields(product, data)
        db.session.commit()
        return jsonify({
            "message": "Product updated successfully",
            "product": {
                "id": product.name,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "image_url": product.image_url,
                "categories": [
                    category.name for category in product.categories.all()
                ],
                "tags": [tag.name for tag in product.tags.all()],
            },
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@update_product_bp.route(
    '/products/<int:product_id>/update',
    methods=['GET', 'POST']
)
def update_product(product_id: int) -> WerkzeugResponse | str:
    """Update a product's details"""
    product = get_by_id(Product, product_id)
    if not product:
        return make_response(jsonify({"message": "Product not found"}), 404)

    if request.method == 'POST':
        product.name = request.form.get('name', product.name)
        product.description = request.form.get(
            'description', product.description
        )
        product.price = float(request.form.get('price', product.price))

        db.session.commit()
        return render_template('product_detail.html', product=product)

    return render_template('update_product.html', product=product)


@update_product_bp.route(
    '/update-product/<int:product_id>',
    methods=['GET', 'POST']
)
def update_product_alt(product_id: int) -> WerkzeugResponse | str:
    """Alternative route for updating a product's details"""
    product = get_by_id(Product, product_id)
    if not product:
        return make_response(jsonify({"message": "Product not found"}), 404)

    if request.method == 'POST':
        product.name = request.form.get('name', product.name)
        product.description = request.form.get(
            'description', product.description)
        product.price = float(request.form.get('price', product.price))

        db.session.commit()
        return redirect(
            url_for('read_product.product_detail', product_id=product.id)
        )

    return render_template('update_product.html', product=product)
