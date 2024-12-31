#!/usr/bin/python3
"""
This module contains the routes for pagination
"""
from flask import Blueprint, jsonify, request
from shophive_packages.models.product import Product
from shophive_packages import db

pagination_bp = Blueprint('pagination', __name__)

@pagination_bp.route("/api/pagination", methods=['GET'], strict_slashes=False)
def get_all_products():
    """
    API endpoint to get paginated products
    """

    limit = request.args.get('limit', type=int)
    # sets default page to 1
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int)
    offset = request.args.get('offset', type=int, default=0)
    # Adding sorting, ordering and filtering
    sort_by = request.args.get('sort_by', default='created_at')
    order_by = request.args.get('order_by', default='desc')
    in_stock = request.args.get('in_stock', type=str)


    # Validate parameters for pagination
    if page <= 0:
        return jsonify({"message": "Page number must be a positive integer"}), 400

    if per_page is not None and per_page <= 0:
        return jsonify({"message": "per_page must be a positive integer"}), 400

    if limit is not None and limit <= 0:
        return jsonify({"message": "limit must be a positive integer"}), 400

    if offset < 0:
        return jsonify({"message": "offset must be a positive integer"}), 400

    # setting pagination values of the request
    if per_page and not limit:
        limit = per_page
    elif not limit:
        limit = 10

    # calculate offset when not set
    if not offset:
        offset = (page - 1) * limit

    # Query the database for products
    try:
        # Retrueve all products with latest to be created coming first
        products_query = db.session.query(Product).order_by(Product.created_at.desc())
        # get product count
        total_products = products_query.count()
        # apply pagination
        products = products_query.offset(offset).limit(limit).all()

        # Handle next and previous page navigation
        total_pages = (total_products + limit - 1) // limit
        next_page = page + 1 if page < total_pages else None
        prev_page = page - 1 if page > 1 else None

        # Handle response
        return jsonify({
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "tags": [tag.name for tag in product.tags],
                    "categories": [category.name for category in product.categories]
                } for product in products
            ],
            "pagination": {
                "total": total_products,
                "limit": limit,
                "page": page,
                "per_page": per_page,
                "offset": offset,
                "total_pages": total_pages,
                "next_page": next_page,
                "prev_page": prev_page
            }
            }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
