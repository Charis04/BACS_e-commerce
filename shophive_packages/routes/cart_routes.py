from flask import (
    jsonify,
    request,
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
)
from flask_restful import Resource

from shophive_packages import db
from shophive_packages.models.cart import Cart
from shophive_packages.models.product import Product

cart_bp = Blueprint("cart_bp", __name__)


@cart_bp.route("/cart", methods=["GET"])
def cart():
    # Initialize session if needed
    if "cart_items" not in session:
        session["cart_items"] = []
        session.permanent = True

    cart_items = session.get("cart_items", [])
    cart_total = sum(item["price"] * item["quantity"] for item in cart_items)
    return render_template(
        "cart.html", cart_items=cart_items, cart_total=cart_total
    )


@cart_bp.route("/cart/update", methods=["POST"])
def update_cart():
    cart_items = session.get("cart_items", [])
    remove_item_id = request.form.get("remove")
    if remove_item_id:
        cart_items = [
            item for item in cart_items
            if str(item["id"]) != remove_item_id
        ]
    else:
        for item in cart_items:
            quantity_key = f"quantity_{item['id']}"
            if quantity_key in request.form:
                item["quantity"] = int(request.form[quantity_key])
    session["cart_items"] = cart_items
    session.modified = True  # Mark session as modified
    return redirect(url_for("cart_bp.cart"))


@cart_bp.route("/cart/add", methods=["POST"])
def add_to_cart():
    form_data = request.form.copy()
    print("Form data:", form_data)
    product_id = form_data.get("product_id")
    if not product_id:
        return redirect(url_for("cart_bp.cart"))

    product = Product.query.get(product_id)
    if not product:
        return redirect(url_for("cart_bp.cart"))

    # Initialize session if needed
    if "cart_items" not in session:
        session["cart_items"] = []
        session.permanent = True

    cart_items = session["cart_items"]
    existing_item = next(
        (
            item for item in cart_items
            if str(item["id"]) == str(product_id)
        ),
        None
    )

    if existing_item:
        existing_item["quantity"] += 1
    else:
        cart_items.append(
            {
                "id": product.id,
                "name": product.name,
                "price": float(product.price),  # Convert Decimal to float
                "quantity": 1,
            }
        )

    # Make sure to update the session
    session["cart_items"] = cart_items
    session.modified = True

    print("Updated session cart_items:", session.get("cart_items"))
    return redirect(url_for("cart_bp.cart"))


class CartResource(Resource):
    """
    Resource for managing shopping cart items.
    """

    def get(self):
        """
        Fetch and return all cart items for the current user.

        Returns:
            JSON response with cart data.
        """
        # Fetch and return cart data
        pass

    def post(self):
        """
        Add a product to the cart.

        Returns:
            JSON response with a success message and status code 201.
        """
        data = request.get_json()
        new_cart_item = Cart(
            user_id=data["user_id"],
            product_id=data["product_id"],
            quantity=data["quantity"],
        )
        db.session.add(new_cart_item)
        db.session.commit()
        return jsonify({"message": "Product added to cart"}), 201

    def put(self, cart_item_id: int):
        """
        Update the quantity of an item in the cart.

        Args:
            cart_item_id (int): The ID of the cart item to update.

        Returns:
            JSON response with a success message.
        """
        data = request.get_json()
        cart_item = Cart.query.get(cart_item_id)
        if not cart_item:
            return jsonify({"message": "Cart item not found"}), 404
        cart_item.quantity = data["quantity"]
        db.session.commit()
        return jsonify({"message": "Cart item updated"})

    def delete(self, cart_item_id: int):
        """
        Remove an item from the cart.

        Args:
            cart_item_id (int): The ID of the cart item to remove.

        Returns:
            Empty response with status code 204.
        """
        cart_item = Cart.query.get(cart_item_id)
        if not cart_item:
            return jsonify({"message": "Cart item not found"}), 404
        db.session.delete(cart_item)
        db.session.commit()
        return "", 204
