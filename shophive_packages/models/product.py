from shophive_packages import db

from sqlalchemy.sql import func
from shophive_packages.models.categories import product_categories
from shophive_packages.models.tags import product_tags


class Product(db.Model):
    """
    Represents a product in the system.

    Attributes:
        id (int): The unique identifier for the product.
        name (str): The name of the product.
        description (str): The description of the product.
        price (float): The price of the product.
    """

    id = db.Column(db.Integer, primary_key=True)
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)  # New column
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # create sorting features for sales and stock available
    sales = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)

    # Foreign keys
    cart_id = db.Column(db.Integer, db.ForeignKey("cart.id"), nullable=True)

    # Relationships
    orders = db.relationship("OrderItem", back_populates="item", lazy="select")
    # establish relationship for Product-Category many to many relationship
    categories = db.relationship(
        "Category",
        secondary="product_categories",
        backref=db.backref("product", lazy="dynamic"),
    )
    # establish arelationship for Product-Tag many to many relationship
    tags = db.relationship(
        "Tag", secondary="product_tags", backref=db.backref(
            "product", lazy="dynamic")
    )

    def __repr__(self) -> str:
        """
        Returns a string representation of the product.

        Returns:
            str: A string representation of the product.
        """
        return f"<Product {self.name} {self.price}>"
