from shophive_packages import db


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
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float(), nullable=False)

    def __repr__(self) -> str:
        """
        Returns a string representation of the product.

        Returns:
            str: A string representation of the product.
        """
        return f"<Product {self.name}>"
