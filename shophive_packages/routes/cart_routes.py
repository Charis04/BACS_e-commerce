from flask import (
    jsonify,
    request,
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    Response,
    make_response,
)
from flask_restful import Resource  # type: ignore
from flask_login import current_user  # type: ignore

from shophive_packages import db
from shophive_packages.models.cart import Cart
from shophive_packages.models.product import Product

cart_bp = Blueprint("cart_bp", __name__)


@cart_bp.route("/cart", methods=["GET"])
def cart() -> str:
    print("\n=== Starting cart view ===")
    print(f"Session before: {dict(session)}")

    try:
        if current_user.is_authenticated:
            cart_items = [item.to_dict() for item in current_user.get_cart()]
            cart_total = current_user.get_cart_total()
        else:
            # Make a copy of the session data to avoid reference issues
            cart_items = list(session.get("cart_items", []))
            cart_total = float(session.get("cart_total", 0.0))

        print(f"Cart items: {cart_items}")
        print(f"Cart total: {cart_total}")
        print(f"Session after: {dict(session)}")

        return render_template(
            "cart.html", cart_items=cart_items, cart_total=cart_total
        )
    except Exception as e:
        print(f"Error in cart view: {str(e)}")
        # Reset session if corrupted
        session["cart_items"] = []
        session["cart_total"] = 0.0
        session.modified = True
        return render_template("cart.html", cart_items=[], cart_total=0.0)


@cart_bp.route("/cart/update", methods=["POST"])
def update_cart() -> "Response":
    breakpoint()  # Debugger will stop here when updating cart
    if current_user.is_authenticated:
        for key, value in request.form.items():
            if key.startswith("quantity_"):
                item_id = int(key.split("_")[1])
                cart_item = Cart.query.get(item_id)
                if cart_item and cart_item.user_id == current_user.id:
                    if (
                        "remove" in request.form
                        and str(item_id) == request.form["remove"]
                    ):
                        db.session.delete(cart_item)
                    else:
                        cart_item.quantity = int(value)
        db.session.commit()
        cart_total = current_user.get_cart_total()
    else:
        cart_items = session.get("cart_items", [])
        remove_item_id = request.form.get("remove")
        if remove_item_id:
            cart_items = [
                item for item in cart_items if str(item["id"]) != remove_item_id
            ]
        else:
            for item in cart_items:
                quantity_key = f"quantity_{item['id']}"
                if quantity_key in request.form:
                    item["quantity"] = int(request.form[quantity_key])

        # Update cart total
        cart_total = sum(
            item["price"] * item["quantity"] for item in cart_items
        )
        session["cart_items"] = cart_items
        session["cart_total"] = cart_total
        session.modified = True
    return make_response(redirect(url_for("cart_bp.cart")))


@cart_bp.route("/cart/add", methods=["POST"])
def add_to_cart() -> Response:
    try:
        product_id = request.form.get("product_id")
        print(f"\n=== Adding product {product_id} to cart ===")
        print(f"Session before: {dict(session)}")

        if not product_id:
            return make_response(redirect(url_for("cart_bp.cart")))

        product = Product.query.get(product_id)
        if not product:
            return make_response(redirect(url_for("cart_bp.cart")))

        if current_user.is_authenticated:
            # ...existing authenticated user code...
            pass
        else:
            # Get a new copy of the cart items
            cart_items = list(session.get("cart_items", []))
            product_id = int(product_id)

            # Find existing item
            existing_item = next(
                (item for item in cart_items if item["id"] == product_id), None
            )

            if existing_item:
                existing_item["quantity"] += 1
            else:
                cart_items.append(
                    {
                        "id": product_id,
                        "name": product.name,
                        "price": float(product.price),
                        "quantity": 1,
                    }
                )

            # Update session with new copies
            session["cart_items"] = cart_items
            session["cart_total"] = sum(
                item["price"] * item["quantity"] for item in cart_items
            )
            session.modified = True

            print(f"Session after: {dict(session)}")

        return make_response(redirect(url_for("cart_bp.cart")))
    except Exception as e:
        print(f"Error adding to cart: {str(e)}")
        return make_response(redirect(url_for("cart_bp.cart")))


class CartResource(Resource):
    """
    Resource for managing shopping cart items.
    """

    def get(self) -> tuple[Response, int]:
        """
        Fetch and return all cart items for the current user.

        Returns:
            JSON response with cart data.
        """
        if current_user.is_authenticated:
            cart_items = [item.to_dict() for item in current_user.get_cart()]
            return jsonify({"cart_items": cart_items}), 200
        return jsonify({"message": "User not authenticated"}), 401

    def post(self) -> tuple[Response, int]:
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

    def put(self, cart_item_id: int) -> tuple[Response, int]:
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
        return jsonify({"message": "Cart item updated"}), 200

    def delete(self, cart_item_id: int) -> tuple[str | Response, int]:
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
