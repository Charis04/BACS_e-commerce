from flask_login import UserMixin  # type: ignore
from flask_bcrypt import (  # type: ignore
    generate_password_hash, check_password_hash)
from shophive_packages import db
from shophive_packages.models.product import Product
from typing import List, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from shophive_packages.models.cart import Cart
else:
    from shophive_packages.models.cart import Cart


class User(UserMixin, db.Model):  # type: ignore[name-defined]
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The password of the user.
        role (str): The role of the user ("buyer" or "seller").
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="buyer")

    # Relationships
    orders = db.relationship("Order", back_populates="buyer", lazy="select")
    carts = db.relationship("Cart", backref="buyer", lazy=True)

    def __init__(
        self,
        username: str,
        email: str,
        password: str | None = None,
        role: str = "buyer"
    ) -> None:
        self.username = username
        self.email = email
        self.role = role
        if password:
            self.set_password(password)

    def __repr__(self) -> str:
        return f"<User {self.username} {self.role}>"

    # Set the password hash
    def set_password(self, password: str) -> None:
        """Hash and set the user's password"""
        if password:
            self.password = generate_password_hash(password).decode('utf-8')

    # Check if the password matches
    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash"""
        if not self.password:
            return False
        return bool(check_password_hash(self.password, password))

    def get_cart(self) -> List[Cart]:
        """Get or create user's cart"""
        print(f"\n=== Getting cart for user {self.username} ===")
        cart_items: List[Cart] = Cart.query.filter_by(user_id=self.id).all()
        print(f"Found {len(cart_items)} cart items")
        return cart_items

    def add_to_cart(self, product: 'Product', quantity: int = 1) -> Cart:
        """Add item to user's cart"""
        cart_item = Cart.query.filter_by(
            user_id=self.id,
            product_id=product.id
        ).first()

        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(
                user_id=self.id,
                product_id=product.id,
                quantity=quantity
            )
            db.session.add(cart_item)

        db.session.commit()
        return cast(Cart, cart_item)

    def get_cart_total(self) -> float:
        """Calculate total price of cart items"""
        print(f"\n=== Calculating cart total for user {self.username} ===")
        cart_items = self.get_cart()
        total = float(sum(
            item.product.price * item.quantity
            for item in cart_items
        ))
        print(f"Cart total calculated: ${total}")
        return total


class Seller(db.Model):  # type: ignore[name-defined]
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Relationships
    orders = db.relationship(
        "OrderItem", back_populates="seller", lazy="select"
    )

    def __repr__(self) -> str:
        """
        Returns a string representation of the user.

        Returns:
            str: A string representation of the user.
        """
        return f"<Seller {self.username} {self.email}>"

    def set_password(self, password: str) -> None:
        """
        Set the user's password to a hashed value.

        Args:
            password (str): The plain-text password.
        """
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Check if the provided password matches the stored hashed password.

        Args:
            password (str): The plain-text password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return bool(check_password_hash(self.password, password))
