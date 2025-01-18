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


class BaseUser(db.Model):  # type: ignore[name-defined]
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(
        self, username: str, email: str, password: str | None = None
    ) -> None:
        self.username = username
        self.email = email
        if password:
            self.set_password(password)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.username}>"

    def set_password(self, password: str) -> None:
        """Hash and set the user's password"""
        if password:
            self.password = generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash"""
        if not self.password:
            return False
        return bool(check_password_hash(self.password, password))


class User(UserMixin, BaseUser):
    __tablename__ = 'user'
    role = db.Column(db.String(10), nullable=False, default="buyer")

    # Relationships
    orders = db.relationship("Order", back_populates="buyer", lazy="select")
    products = db.relationship(
        "Product",
        foreign_keys='Product.seller_id',
        back_populates="seller",
        lazy="select"
    )
    carts = db.relationship("Cart", backref="buyer", lazy=True)

    def __init__(
        self,
        username: str,
        email: str,
        password: str | None = None,
        role: str = "buyer"
    ) -> None:
        super().__init__(username, email, password)
        self.role = role

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


class Seller(BaseUser):
    __tablename__ = 'seller'

    # Relationships
    orders = db.relationship(
        "OrderItem", back_populates="seller", lazy="select"
    )
