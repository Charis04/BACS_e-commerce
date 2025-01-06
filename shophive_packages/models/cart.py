from shophive_packages import db


class Cart(db.Model):
    """
    Represents a shopping cart item.

    Attributes:
        id (int): The unique identifier for the cart item.
        user_id (int): The ID of the user who owns the cart item.
        product_id (int): The ID of the product in the cart.
        quantity (int): The quantity of the product in the cart.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    # Removed product id foreign key and created relationship instead
    quantity = db.Column(db.Integer, default=1)

    # Relationships
    products = db.relationship("Product", backref='cart')

    def __repr__(self) -> str:
        return f"<Cart {self.id}>"
