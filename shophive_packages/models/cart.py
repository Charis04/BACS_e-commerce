from shophive_packages import db
from flask import session  # noqa: F401


class Cart(db.Model):  # type: ignore[name-defined]
    """Cart model representing a user's shopping cart"""

    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(
        db.Integer, db.ForeignKey("product.id"), nullable=False
    )
    quantity = db.Column(db.Integer, default=1)

    # Define relationships
    product = db.relationship(
        "Product",
        foreign_keys=[product_id],
        backref=db.backref("carts", lazy=True),
    )

    # Define user relationship using back_populates
    user = db.relationship(
        'User',
        back_populates='carts'
    )

    def __init__(
        self, user_id: int, product_id: int, quantity: int = 1
    ) -> None:
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

    def __repr__(self) -> str:
        return f"<Cart {self.id}>"

    def update_quantity(self, quantity: int) -> None:
        """Update item quantity"""
        if quantity <= 0:
            db.session.delete(self)
        else:
            self.quantity = quantity
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def total_amount(self) -> float:
        """Calculate total amount of cart items"""
        return sum([item.product.price * item.quantity for item in self])

    def to_dict(self) -> dict | None:
        """Convert cart item to dictionary"""
        try:
            result = {
                "id": self.id,
                "product_id": self.product_id,
                "name": self.product.name,
                "price": float(self.product.price),
                "quantity": self.quantity,
                "total": float(self.product.price * self.quantity)
            }
            return result
        except Exception:
            return None
