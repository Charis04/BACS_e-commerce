from shophive_packages import db
from flask import session  # noqa


class Cart(db.Model):  # type: ignore[name-defined]
    """Cart model representing a user's shopping cart"""

    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(
        db.Integer, db.ForeignKey("product.id"), nullable=False
    )
    quantity = db.Column(db.Integer, default=1)

    # Define relationship with explicit foreign keys
    product = db.relationship(
        "Product",
        foreign_keys=[product_id],
        backref=db.backref("carts", lazy=True),
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
        print(f"\n=== Updating quantity for cart item {self.id} ===")
        print(f"Old quantity: {self.quantity}, New quantity: {quantity}")
        self.quantity = quantity
        db.session.commit()
        print("Quantity updated successfully")

    def to_dict(self) -> dict | None:
        """Convert cart item to dictionary"""
        print(f"\n=== Converting cart item {self.id} to dict ===")
        try:
            result = {
                "id": self.id,
                "product_id": self.product_id,
                "name": self.product.name,
                "price": float(self.product.price),
                "quantity": self.quantity,
                "total": float(self.product.price * self.quantity)
            }
            print(f"Cart item data: {result}")
            return result
        except Exception as e:
            print(f"Error converting cart item to dict: {str(e)}")
            return None
