from shophive_packages import db
from shophive_packages.models import Cart, User, Product
from flask.testing import FlaskClient


def test_cart_operations(client: FlaskClient) -> None:
    """Test cart model operations."""
    # Create test user and product
    user = User(username="cartuser", email="cart@test.com")
    user.set_password("testpass")
    product = Product(name="Test Product", price=10.00)
    db.session.add_all([user, product])
    db.session.commit()

    # Test cart creation
    cart = Cart(user_id=user.id, product_id=product.id, quantity=1)
    db.session.add(cart)
    db.session.commit()

    # Test updating quantity
    cart.update_quantity(3)
    assert cart.quantity == 3
