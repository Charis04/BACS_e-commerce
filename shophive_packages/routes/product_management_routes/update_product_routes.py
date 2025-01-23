#!/usr/bin/python3
"""
This module contains the routes for updating a product in the catalog
"""
from flask import Blueprint, jsonify, request
from shophive_packages.models.product import Product
from shophive_packages import db
from shophive_packages.models.tags import Tag
from shophive_packages.models.categories import Category
from shophive_packages.routes.product_management_routes.decorators \
    import role_required


update_product_bp = Blueprint('update_product', __name__)


@update_product_bp.route(
    "/api/products/<int:product_id>", methods=['PUT'], strict_slashes=False)
@role_required("seller")
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
    tags = data.get('tags', [])
    categories = data.get('categories', [])
    image_url = data.get('image_url')

    if not any([name, description, price, tags, categories, image_url]):
        return jsonify({"message": "Missing required fields"}), 400

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
    if image_url:
        product.image_url = image_url
    if tags:
        product.tags = []
        for tag_name in tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            product.tags.append(tag)
    if categories:
        product.categories = []
        for category_name in categories:
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)
            product.categories.append(category)

    # committing the changes to the database
    try:
        db.session.commit()
        return jsonify({
            "message": "Product updated successfully",
            "product": {
                "id": product.name,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "image_url": product.image_url,
                "categories": [category.name for category in product.categories],
                "tags": [tag.name for tag in product.tags]
            }
        }), 200

    except Exception as e:
        # reverse the update if there is an error
        db.session.rollback()
        return jsonify({"message": str(e)}), 500
