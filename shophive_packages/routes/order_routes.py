from flask import (
    request, jsonify, render_template, Blueprint, Response, redirect, url_for)
from flask_login import login_required, current_user  # type: ignore
from shophive_packages import db
from shophive_packages.models import Order, OrderItem


order_bp = Blueprint('order_bp', __name__)


def calculate_total(items: list[dict]) -> float:
    """
    Calculates the total amount of an order
    """
    total_amount = 0.0
    for item in items:
        price = item["price"] * item["quantity"]
        total_amount += price

    return total_amount


@order_bp.route("/api/orders", methods=["GET"], strict_slashes=False)
def get_orders() -> tuple[Response, int]:
    """Retrieves all orders"""
    orders = Order.query.all()
    orders_list = [
        {
            "order_id": order.id,
            "buyer_id": order.buyer_id,
            "status": order.status,
            "items": [
                {
                    "name": item.id,
                    "quantity": item.quantity,
                    "price": item.price,
                }
                for item in order.items
            ],
            "total_amount": order.total_amount,
        }
        for order in orders
    ]

    return jsonify({"status": "success", "data": orders_list}), 200


@order_bp.route("/api/orders", methods=["POST"], strict_slashes=False)
def create_order() -> tuple[Response, int]:
    data = request.get_json()
    # Remember to add logic to check if user id exists
    user_id = data.get("user_id")
    items = data.get("items")

    # Logic for creating order and calculating total amount
    order = Order(buyer_id=user_id, total_amount=calculate_total(items))
    db.session.add(order)
    db.session.commit()

    # Add order items
    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            price=item["price"],
            seller_id=1,
        )
        db.session.add(order_item)
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "order_id": order.id,
                    "total_amount": order.total_amount,
                    "status": order.status,
                },
                "message": "Order created successfully.",
            }
        ),
        201,
    )


@order_bp.route(
    "/api/orders/<int:order_id>",
    methods=["GET"],
    strict_slashes=False
)
def get_order(order_id: int) -> tuple[Response, int]:
    """Retrieve details of a specific order."""
    order = Order.query.get_or_404(order_id)
    items = [
        {
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price": item.price,
        }
        for item in order.items
    ]

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "order_id": order.id,
                    "buyer_id": order.buyer_id,
                    "status": order.status,
                    "items": items,
                    "total_amount": order.total_amount,
                },
            }
        ),
        200,
    )


@order_bp.route(
    "/api/orders/<int:order_id>", methods=["PATCH"], strict_slashes=False
)
def update_order_status(order_id: int) -> tuple[Response, int]:
    """Update the status of an order."""
    data = request.get_json()
    status = data.get("status")

    order = Order.query.get_or_404(order_id)
    order.status = status

    """# Add to order history
    history = OrderHistory(order_id=order.id, status=status)
    db.session.add(history)"""

    db.session.commit()
    return (
        jsonify(
            {
                "status": "success",
                "message": "Order status updated successfully.",
            }
        ),
        200,
    )


@order_bp.route(
    "/api/orders/<int:order_id>/status",
    methods=["GET"],
    strict_slashes=False
)
def get_order_status(order_id: int) -> tuple[Response, int]:
    """Endpoints for customers to track their orders."""
    order = Order.query.get_or_404(order_id)
    return (
        jsonify(
            {
                "status": "success",
                "data": {"order_id": order.id, "current_status": order.status},
            }
        ),
        200,
    )


@order_bp.route(
    "/api/user/<int:user_id>/orders",
    methods=["GET"],
    strict_slashes=False
)
def get_user_orders(user_id: int) -> tuple[Response, int]:
    """Get all orders for a specific user"""
    orders = Order.query.filter_by(buyer_id=user_id).all()
    return jsonify({
        "status": "success",
        "data": [{
            "order_id": order.id,
            "status": order.status,
            "total_amount": order.total_amount,
        } for order in orders]
    }), 200


@order_bp.route(
    '/api/user/<int:user_id>/orders',
    methods=['GET'],
    strict_slashes=False
)
def get_buyer_orders(user_id: int) -> tuple[Response, int]:
    """Endpoint to get a buyer's orders"""
    orders = Order.query.filter_by(buyer_id=user_id).all()
    return jsonify({
        "status": "success",
        "data": [{
            "order_id": o.id,
            "status": o.status,
            "total_amount": o.total_amount,
            } for o in orders]
    }), 200


@order_bp.route(
    "/api/sellers/<int:seller_id>/orders",
    methods=["GET"],
    strict_slashes=False
)
def get_seller_orders(seller_id: int) -> tuple[Response, int]:
    """Endpoints for sellers to manage orders."""
    orders = OrderItem.query.filter_by(seller_id=seller_id).all()
    return (
        jsonify(
            {
                "status": "success",
                "data": [
                    {
                        "order_id": o.id,
                        "status": o.status,
                        "product_id": o.product_id,
                        "total_amount": o.price * o.quantity,
                    }
                    for o in orders
                ],
            }
        ),
        200,
    )
    return jsonify({
        "status": "success",
        "data": [{
            "order_id": o.id,
            "status": o.status,
            "product_id": o.product_id,
            "total_amount": o.price * o.quantity,
            } for o in orders]
    }), 200


@order_bp.route('/orders', methods=['GET'], strict_slashes=False)
def orders() -> str:
    user_id = 1  # current_user.id
    role = 'buyer'  # current_user.role
    if role == 'buyer':
        response, _ = get_buyer_orders(user_id)
        orders = response.get_json()['data']
    else:
        response, _ = get_seller_orders(user_id)
        orders = response.get_json()['data']

    return render_template('seller_orders.html', orders=orders)


@order_bp.route('/seller/orders')
@login_required  # type: ignore
def view_seller_orders():
    """View orders for sellers"""
    if current_user.role != 'seller':
        return redirect(url_for('home_bp.home'))
    orders = Order.query.filter_by(seller_id=current_user.id).all()
    return render_template('seller_orders.html', orders=orders)


@order_bp.route('/buyer/orders')
@login_required  # type: ignore
def view_buyer_orders():
    """View orders for buyers"""
    if current_user.role != 'buyer':
        return redirect(url_for('home_bp.home'))
    orders = Order.query.filter_by(buyer_id=current_user.id).all()
    return render_template('buyer_orders.html', orders=orders)
