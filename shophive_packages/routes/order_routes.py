from flask import request, jsonify
from shophive_packages import db, app
from shophive_packages.models import Order, OrderItem


def calculate_total(items):
    """
    Calculates the total amount of an order
    """
    total_amount = 0.0
    for item in items:
        price = item["price"] * item["quantity"]
        total_amount += price

    return total_amount


@app.route("/api/orders", methods=["GET"], strict_slashes=False)
def get_orders():
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


@app.route("/api/orders", methods=["POST"], strict_slashes=False)
def create_order():
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


@app.route("/api/orders/<int:order_id>", methods=["GET"], strict_slashes=False)
def get_order(order_id):
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


@app.route(
    "/api/orders/<int:order_id>", methods=["PATCH"], strict_slashes=False
)
def update_order_status(order_id):
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


@app.route(
    "/api/orders/<int:order_id>/status",
    methods=["GET"],
    strict_slashes=False
)
def get_order_status(order_id):
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


@app.route(
    "/api/user/<int:user_id>/orders",
    methods=["GET"],
    strict_slashes=False
)
def get_user_orders(user_id):
    pass


@app.route(
    "/api/sellers/<int:seller_id>/orders",
    methods=["GET"],
    strict_slashes=False
)
def get_seller_orders(seller_id):
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
