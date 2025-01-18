from typing import Optional, TypeVar, Union, cast
from flask import session
from shophive_packages.models.user import User, Seller
from shophive_packages.models.product import Product

UserType = TypeVar("UserType", User, Seller)


def find_user(username: str) -> Optional[Union[User, Seller]]:
    """Find user in either User or Seller table"""
    # Try to find by username first
    user = Seller.query.filter_by(username=username).first()
    if user:
        return cast(Seller, user)

    user = User.query.filter_by(username=username).first()
    if user:
        return cast(User, user)

    # Then try by email
    user = Seller.query.filter_by(email=username).first()
    if user:
        return cast(Seller, user)

    user = User.query.filter_by(email=username).first()
    if user:
        return cast(User, user)

    return None


def merge_guest_cart(user: User) -> None:
    """Merge guest cart items into user's cart"""
    guest_cart = session.get("cart_items", [])
    if guest_cart:
        for item in guest_cart:
            product = Product.query.get(item["product_id"])
            if product:
                user.add_to_cart(product, item["quantity"])
        # Clear guest cart
        session.pop("cart_items", None)
        session.pop("cart_total", None)
