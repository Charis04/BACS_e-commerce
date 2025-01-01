# tests/test_models/test_product_model.py
import pytest  # noqa
from shophive_packages import db
from shophive_packages.models import Product


def test_product_model_repr():
    """
    Test the string representation of the Product model.

    Asserts:
        The string representation matches the expected format.
    """
    product = Product(name="Test Product", description="Sample", price=10.99)
    assert str(product) == "<Product Test Product>"


def test_product_creation(client):
    """
    Test the creation of a Product in the database.

    Args:
        client (FlaskClient): The test client.

    Asserts:
        The product count is 1 after addition.
        The added product's name is "Laptop".
    """
    product = Product(name="Laptop", description="Gaming laptop",
                      price=1500.00)
    db.session.add(product)
    db.session.commit()
    assert Product.query.count() == 1
    assert Product.query.first().name == "Laptop"
