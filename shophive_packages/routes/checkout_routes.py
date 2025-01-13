from flask import Blueprint, render_template, request, redirect, url_for, \
    session

checkout_bp = Blueprint("checkout_bp", __name__)


@checkout_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        # Process payment and clear the cart
        session.pop("cart_items", None)
        return redirect(url_for("home_bp.home"))
    cart_total = session.get("cart_total", 0)
    return render_template("checkout.html", cart_total=cart_total)
