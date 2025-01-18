#!/usr/bin/python3
"""
This module contains the routes for pagination
"""
from flask import Blueprint, jsonify, request
from shophive_packages.models.product import Product
from shophive_packages import db

pagination_bp = Blueprint("pagination", __name__)


@pagination_bp.route("/api/pagination", methods=["GET"], strict_slashes=False)
def get_all_products():
    """
    API endpoint to get paginated products
    """

    limit = request.args.get("limit", type=int)
    # sets default page to 1
    page = request.args.get("page", type=int, default=1)
    # Adding sorting, ordering and filtering
    sort_by = request.args.get("sort_by", default="created_at")
    order_by = request.args.get("order_by", default="desc")
    in_stock = request.args.get("in_stock", type=str)

    # Validate parameters for pagination
    if page <= 0:
        return jsonify({"message":
                        "Page number must be a positive integer"}), 400

    if limit is not None and limit <= 0:
        return jsonify({"message": "limit must be a positive integer"}), 400

    # setting pagination values of the request
    if not limit:
        limit = 10

    # calculate offset when not set
    offset = (page - 1) * limit

    # Query the database for products
    try:
        products_query = db.session.query(Product)
        # make stock filter
        if in_stock == "true":
            products_query = products_query.filter(Product.quantity > 0)
        elif in_stock == "false":
            products_query = products_query.filter(Product.quantity == 0)

        # make sorting
        available_sort_fields = {
            "created_at": Product.created_at,
            "name": Product.name,
            "sales": Product.sales,
            "price": Product.price,
        }
        if not available_sort_fields.get(sort_by):
            return jsonify({"message": "Invalid sorting field"}), 400
        sort_fields = available_sort_fields.get(sort_by, Product.created_at)
        if not sort_fields:
            return jsonify({"message": "Invalid sorting field"}), 400

        sort_order = sort_fields.desc() if order_by == "desc"\
            else sort_fields.asc()
        products_query = products_query.order_by(sort_order)

        # get product count
        total_products = products_query.count()
        # apply pagination
        products = products_query.offset(offset).limit(limit).all()

        # Handle next and previous page navigation
        total_pages = (total_products + limit - 1) // limit
        next_page = page + 1 if page < total_pages else None
        prev_page = page - 1 if page > 1 else None

        # Handle response
        return (
            jsonify(
                {
                    "products": [
                        {
                            "id": product.id,
                            "name": product.name,
                            "description": product.description,
                            "price": product.price,
                            "sales": product.sales,
                            "quantity": product.quantity,
                            "tags": [tag.name for tag in product.tags],
                            "categories": [
                                cat.name for cat in product.categories
                            ],
                        }
                        for product in products
                    ],
                    "pagination": {
                        "total": total_products,
                        "limit": limit,
                        "page": page,
                        "offset": offset,
                        "total_pages": total_pages,
                        "next_page": next_page,
                        "prev_page": prev_page,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"message": str(e)}), 500
