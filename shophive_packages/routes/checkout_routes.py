from flask import Blueprint, render_template, request, redirect, url_for, \
    session, Response as FlaskResponse, make_response

checkout_bp = Blueprint("checkout_bp", __name__)


@checkout_bp.route("/checkout", methods=["GET", "POST"])
def checkout() -> FlaskResponse:
    """Checkout route for processing payments"""
    if request.method == "POST":
        # Process payment and clear the cart
        session.pop("cart_items", None)
        return make_response(redirect(url_for("home_bp.home")))
    cart_total = session.get("cart_total", 0)
    return make_response(
        render_template("checkout.html", cart_total=cart_total)
    )
