from flask import (
    request,
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    Response,
    make_response,
    current_app,
    jsonify
)
from typing import Union, Callable, TypeVar  # noqa
from flask_restful import Resource  # type: ignore
from flask_login import current_user, login_required  # type: ignore
from shophive_packages import db
from shophive_packages.models.cart import Cart
from shophive_packages.models.product import Product
from shophive_packages.db_utils import get_by_id

F = TypeVar('F', bound=Callable)

cart_bp = Blueprint("cart_bp", __name__)


def get_cart_count() -> int:
    """Get the number of items in cart."""
    if current_user.is_authenticated:
        return sum(item.quantity for item in current_user.get_cart())
    return sum(item['quantity'] for item in session.get("cart_items", []))


@cart_bp.before_app_request
def inject_cart_count() -> None:
    """Make cart count available to all templates."""
    current_app.jinja_env.globals['cart_count'] = get_cart_count()


@cart_bp.route("/cart", methods=["GET"])
def cart() -> str:
    """
    Display the shopping cart.

    Returns:
        The rendered cart template.
    """
    if current_user.is_authenticated:
        cart_items = [item.to_dict() for item in current_user.get_cart()]
        cart_total = current_user.get_cart_total()
    else:
        cart_items = session.get("cart_items", [])
        cart_total = session.get("cart_total", 0)

    return render_template(
        "cart.html", cart_items=cart_items, cart_total=cart_total
    )


@cart_bp.route("/cart/update", methods=["POST"])
def update_cart() -> Response:
    """
    Update the shopping cart.

    Returns:
        A redirect response to the cart page.
    """
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
                item for item in cart_items
                if str(item["id"]) != remove_item_id
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


@cart_bp.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required  # type: ignore[misc]
def add_to_cart(product_id: int) -> tuple[Response, int]:
    """Add a product to cart"""
    try:
        product = get_by_id(Product, product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        json_data = request.get_json() or {}
        quantity = json_data.get('quantity', 1)

        cart_item = Cart.query.filter_by(
            user_id=current_user.id,
            product_id=product.id
        ).first()

        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)

        db.session.commit()
        return jsonify({"message": "Added to cart"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@cart_bp.route("/cart/remove/<int:product_id>", methods=["DELETE"])
@login_required  # type: ignore[misc]
def remove_from_cart(product_id: int) -> tuple[Response, int]:
    """Remove a product from cart"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    try:
        cart_item = Cart.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first_or_404()

        db.session.delete(cart_item)
        db.session.commit()

        return jsonify({"message": "Item removed from cart"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


class CartResource(Resource):
    """
    Resource for managing shopping cart items.
    """

    def get(self) -> tuple[dict, int]:
        """
        Fetch and return all cart items for the current user.

        Returns:
            JSON response with cart data.
        """
        # Fetch and return cart data
        cart_items = [item.to_dict() for item in Cart.query.all()]
        return {"cart_items": cart_items}, 200

    def post(self) -> tuple[dict, int]:
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
        return {"message": "Product added to cart"}, 201

    def put(self, cart_item_id: int) -> tuple[dict, int]:
        """
        Update the quantity of an item in the cart.

        Args:
            cart_item_id (int): The ID of the cart item to update.

        Returns:
            JSON response with a success message.
        """
        data = request.get_json()
        cart_item = get_by_id(Cart, cart_item_id)
        if not cart_item:
            return {"message": "Cart item not found"}, 404
        cart_item.quantity = data["quantity"]
        db.session.commit()
        return {"message": "Cart item updated"}, 200

    def delete(self, cart_item_id: int) -> tuple[dict | str, int]:
        """
        Remove an item from the cart.

        Args:
            cart_item_id (int): The ID of the cart item to remove.

        Returns:
            Empty response with status code 204.
        """
        cart_item = get_by_id(Cart, cart_item_id)
        if not cart_item:
            return {"message": "Cart item not found"}, 404
        db.session.delete(cart_item)
        db.session.commit()
        return "", 204
