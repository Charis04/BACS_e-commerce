#!/usr/bin/python3
"""
This module contains the routes for adding a new product to the catalog
"""

from flask import Blueprint, jsonify, request
from shophive_packages.models.product import Product
from shophive_packages.models.tags import Tag
from shophive_packages.models.categories import Category
from shophive_packages import db
from shophive_packages.routes.product_management_routes.decorators \
    import role_required

new_product_bp = Blueprint('new_product', __name__)


@new_product_bp.route("/api/products", methods=['POST'], strict_slashes=False)
@role_required('seller')
def add_product():
    """
    Api endpoint to add a product to the catalog
    It accepts product details via Json payload and saves them to the database
    """
    # Parse the json payload
    data = request.get_json()
    # Check if the payload is empty
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    tags = data.get('tags', [])
    categories = data.get('categories', [])
    image_url = data.get('image_url')

    # Validating the data
    if not name or not description or not price:
        return jsonify({"message": "Missing required fields"}), 400

    if not isinstance(price, (int, float)) or price <= 0:
        return jsonify({"message": "Price must be a positive number"}), 400

    try:
        # Creating the new product instance
        new_product = Product(name=name, description=description, price=price,
                              image_url=image_url)
        # Handle tags
        for tag_name in tags:
            # Check if the tag already exists in the database
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                # If the tag doesn't exist, create a new Tag instance
                tag = Tag(name=tag_name)
                db.session.add(tag)
            # Add the tag to the product
            new_product.tags.append(tag)

        # Handle categories
        for category_name in categories:
            # Check if the category already exists in the database
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                # If the category doesn't exist, create a new Tag instance
                category = Category(name=category_name)
                db.session.add(category)
            # Add the category to the product
            new_product.categories.append(category)

        # Adding the new product to the database
        db.session.add(new_product)
        db.session.commit()
        return jsonify(
            {
                "message": "Product added successfully",
                "product": {
                    "id": new_product.id,
                    "name": new_product.name,
                    "description": new_product.description,
                    "price": new_product.price,
                    "tags": [{"id": tag.id, "name": tag.name} for tag in new_product.tags],
                    "categories": [{"id": category.id, "name": category.name}
                           for category in new_product.categories],
                    "created_at": new_product.created_at,
                    "updated_at": new_product.updated_at,
                    "image_url": new_product.image_url

                }
            }), 201
    except Exception as e:
        db.session.rollback()  # reverse the transaction if an error occurs
        # Return an internal server error
        return jsonify({"message": str(e)}), 500
