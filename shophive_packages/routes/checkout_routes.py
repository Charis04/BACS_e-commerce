from flask import Blueprint, render_template, request, redirect, url_for, \
    session, Response as FlaskResponse, make_response, flash
from flask_login import login_required, current_user  # type: ignore
from shophive_packages import db
from shophive_packages.models.orders import Order, OrderItem

checkout_bp = Blueprint("checkout_bp", __name__)

@checkout_bp.route("/checkout", methods=["GET", "POST"])
@login_required  # type: ignore[misc]
def checkout() -> FlaskResponse:
    """Checkout route for processing payments"""
    # Prevent sellers from accessing checkout
    if not hasattr(current_user, 'get_cart'):
        flash('Sellers do not have access to checkout functionality', 'error')
        return make_response(redirect(url_for('home_bp.home')))

    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("Please login to complete your purchase", "warning")
            return make_response(redirect(url_for("user_bp.login")))

        # Create order
        cart = current_user.get_cart()
        order = Order(buyer_id=current_user.id)
        for item in cart:
            order.add_item(item, address=request.form.get("address"))
            db.session.delete(item)
        db.session.add(order)

        # Process payment and clear the cart
        session.pop("cart_items", None)
        session.pop("cart_total", None)
        db.session.commit()
        flash("Order successfully placed!", "success")
        return make_response(redirect(url_for("home_bp.home")))

    cart_total = session.get("cart_total", 0)
    return make_response(
        render_template("checkout.html", cart_total=cart_total)
    )
