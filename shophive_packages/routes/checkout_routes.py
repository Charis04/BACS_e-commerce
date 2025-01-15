from flask import Blueprint, render_template, request, redirect, url_for, \
    session, Response as FlaskResponse, make_response, flash
from flask_login import login_required, current_user  # type: ignore

checkout_bp = Blueprint("checkout_bp", __name__)


@checkout_bp.route("/checkout", methods=["GET", "POST"])
@login_required  # type: ignore[misc]
def checkout() -> FlaskResponse:
    """Checkout route for processing payments"""
    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("Please login to complete your purchase", "warning")
            return make_response(redirect(url_for("user_bp.login")))

        # Process payment and clear the cart
        session.pop("cart_items", None)
        return make_response(redirect(url_for("home_bp.home")))

    cart_total = session.get("cart_total", 0)
    return make_response(
        render_template("checkout.html", cart_total=cart_total)
    )
