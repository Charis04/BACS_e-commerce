from flask import (
    request,
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    Response,  # This is Flask's Response
    make_response,
    current_app,
    jsonify,
    flash
)
from typing import Union, Callable, TypeVar  # noqa
from flask_restful import Resource  # type: ignore
from flask_login import current_user, login_required  # type: ignore
from shophive_packages import db
from shophive_packages.models.cart import Cart
from shophive_packages.models.product import Product
from shophive_packages.db_utils import get_by_id
from flask_wtf import FlaskForm  # type: ignore # noqa
from shophive_packages.forms.forms import CartForm

F = TypeVar('F', bound=Callable)

cart_bp = Blueprint("cart_bp", __name__)

# Remove the old CartForm class definition
# class CartForm(FlaskForm):
#     """Form for CSRF protection"""
#     pass


def get_cart_count() -> int:
    """Get the number of items in cart."""
    if current_user.is_authenticated and hasattr(current_user, 'get_cart'):
        return sum(item.quantity for item in current_user.get_cart())
    cart_items = session.get('cart_items', [])
    return sum(item['quantity'] for item in cart_items)


@cart_bp.before_app_request
def inject_cart_count() -> None:
    """Make cart count available to all templates."""
    # Only inject cart data for buyers or anonymous users
    if not current_user.is_authenticated or hasattr(current_user, 'get_cart'):
        current_app.jinja_env.globals['cart_count'] = get_cart_count()
        if current_user.is_authenticated and hasattr(current_user, 'get_cart'):
            cart_items = current_user.get_cart()
            total = current_user.get_cart_total()
        else:
            cart_items = session.get('cart_items', [])
            total = sum(
                Product.query.get(item['product_id']).price * item['quantity']
                for item in cart_items
                if Product.query.get(item['product_id'])
            )
        current_app.jinja_env.globals['cart_total'] = total
    else:
        # Set empty cart data for sellers
        current_app.jinja_env.globals['cart_count'] = 0
        current_app.jinja_env.globals['cart_total'] = 0


def _get_or_create_cart() -> list:
    """Get cart from session for guest users or database for
    authenticated users"""
    if current_user.is_authenticated:
        return list(current_user.get_cart())
    return session.get('cart_items', [])


def _save_cart(cart_items: list) -> None:
    """Save cart to session for guest users or database for
    authenticated users"""
    if not current_user.is_authenticated:
        session['cart_items'] = cart_items


def _handle_remove_item(product_id: int, user_id: int) -> None:
    """Remove an item from cart."""
    cart_item = Cart.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()


def _update_item_quantity(
    product_id: int,
    user_id: int,
    new_quantity: int
) -> None:
    """Update quantity of an item in cart."""
    if new_quantity <= 0:
        return
    cart_item = Cart.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()
    if cart_item:
        cart_item.quantity = new_quantity
        db.session.commit()


def _update_guest_cart(form_data: dict) -> list:
    """Update guest user's cart from form data."""
    cart_items = session.get('cart_items', [])
    updated_cart = []

    if "remove" in form_data:
        product_id = int(form_data["remove"])
        return [item for item in cart_items
                if item['product_id'] != product_id]

    for item in cart_items:
        quantity_key = f"quantity_{item['product_id']}"
        if quantity_key in form_data:
            new_quantity = int(form_data[quantity_key])
            if new_quantity > 0:
                item['quantity'] = new_quantity
                updated_cart.append(item)

    return updated_cart


@cart_bp.route("/cart", methods=["GET"])
def cart() -> Response:
    """
    Display the shopping cart.

    Returns:
        The rendered cart template.
    """
    # Prevent sellers from accessing cart
    if current_user.is_authenticated and not hasattr(current_user, 'get_cart'):
        flash('Sellers do not have access to shopping cart functionality',
              'error')
        return make_response(redirect(url_for('home_bp.home')))

    if current_user.is_authenticated:
        cart_items = current_user.get_cart()
        products = [(item.product, item.quantity) for item in cart_items]
        total = current_user.get_cart_total()
    else:
        cart_items = session.get('cart_items', [])
        products = []
        total = 0
        for item in cart_items:
            product = Product.query.get(item['product_id'])
            if product:
                products.append((product, item['quantity']))
                total += product.price * item['quantity']

    form = CartForm()
    return make_response(
        render_template(
            'cart.html',
            cart_items=products,
            total=total,
            form=form
        )
    )


@cart_bp.route("/cart/update", methods=["POST"])
def update_cart() -> Response:
    """Update the shopping cart."""
    try:
        if current_user.is_authenticated:
            if "remove" in request.form:
                _handle_remove_item(
                    int(request.form["remove"]),
                    current_user.id
                )
                return make_response(redirect(url_for("cart_bp.cart")))

            # Handle quantity updates
            for key, value in request.form.items():
                if key.startswith("quantity_"):
                    product_id = int(key.split("_")[1])
                    _update_item_quantity(
                        product_id,
                        current_user.id,
                        int(value)
                    )
        else:
            # Handle guest cart updates
            updated_cart = _update_guest_cart(request.form)
            session['cart_items'] = updated_cart
            session.modified = True

    except (ValueError, Exception):
        db.session.rollback()

    return make_response(redirect(url_for("cart_bp.cart")))


@cart_bp.route("/cart/add", methods=["POST"])
def add_to_cart() -> Response:
    """Add item to cart for both guest and authenticated users"""
    # Prevent sellers from adding to cart
    if current_user.is_authenticated and not hasattr(current_user, 'get_cart'):
        return make_response(
            jsonify({"message": "Sellers cannot add items to cart"}),
            403
        )

    product_id = request.form.get("product_id")
    if not product_id:
        return make_response(
            jsonify({"message": "Product ID is required"}),
            400
        )

    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get("quantity", 1))
    next_page = (
        request.form.get('next')
        or request.referrer
        or url_for('home_bp.home')
    )

    try:
        if current_user.is_authenticated:
            current_user.add_to_cart(product, quantity)
        else:
            cart_items = session.get('cart_items', [])
            item_exists = False
            for item in cart_items:
                if item['product_id'] == int(product_id):
                    item['quantity'] += quantity
                    item_exists = True
                    break
            if not item_exists:
                cart_items.append({
                    'product_id': int(product_id),
                    'quantity': quantity
                })
            session['cart_items'] = cart_items

        flash(f'Added {product.name} to cart!', 'success')
        return make_response(redirect(next_page))

    except Exception:
        flash('Error adding item to cart', 'error')
        return make_response(redirect(next_page))


@cart_bp.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required  # type: ignore[misc]
def add_to_cart_api(product_id: int) -> Response:
    """Add a product to cart via API"""
    try:
        product = get_by_id(Product, product_id)
        if not product:
            return make_response(
                jsonify({"error": "Product not found"}),
                404
            )
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
        return make_response(
            jsonify({"message": "Added to cart"}),
            200
        )
    except Exception as e:
        db.session.rollback()
        return make_response(
            jsonify({"error": str(e)}),
            500
        )


@cart_bp.route("/cart/remove/<int:product_id>", methods=["DELETE"])
@login_required  # type: ignore[misc]
def remove_from_cart(product_id: int) -> Response:
    """Remove a product from cart"""
    if not current_user.is_authenticated:
        return make_response(
            jsonify({"error": "Authentication required"}),
            401
        )

    try:
        cart_item = Cart.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first_or_404()

        db.session.delete(cart_item)
        db.session.commit()

        return make_response(
            jsonify({"message": "Item removed from cart"}),
            200
        )
    except Exception as e:
        db.session.rollback()
        return make_response(
            jsonify({"error": str(e)}),
            500
        )


class CartResource(Resource):
    """
    Resource for managing shopping cart items.
    """

    def get(self) -> Response:
        """
        Fetch and return all cart items for the current user.

        Returns:
            JSON response with cart data.
        """
        # Fetch and return cart data
        cart_items = [item.to_dict() for item in Cart.query.all()]
        return make_response(jsonify({"cart_items": cart_items}), 200)

    def post(self) -> Response:
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
        return make_response(
            jsonify({"message": "Product added to cart"}),
            201
        )

    def put(self, cart_item_id: int) -> Response:
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
            return make_response(
                jsonify({"message": "Cart item not found"}),
                404
            )
        cart_item.quantity = data["quantity"]
        db.session.commit()
        return make_response(
            jsonify({"message": "Cart item updated"}),
            200
        )

    def delete(self, cart_item_id: int) -> Response:
        """
        Remove an item from the cart.

        Args:
            cart_item_id (int): The ID of the cart item to remove.

        Returns:
            Empty response with status code 204.
        """
        cart_item = get_by_id(Cart, cart_item_id)
        if not cart_item:
            return make_response(
                jsonify({"message": "Cart item not found"}),
                404
            )
        db.session.delete(cart_item)
        db.session.commit()
        return Response(status=204)
