from flask.testing import FlaskClient
from shophive_packages.models.cart import Cart


def test_add_to_cart(
    client: FlaskClient,
    test_user: dict,
    test_product: Cart
) -> None:
    """Test adding an item to cart."""
    client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })

    response = client.post(
        f'/cart/add/{test_product.id}',
        json={'quantity': 1}
    )
    assert response.status_code == 200
    assert Cart.query.count() == 1


def test_view_cart(client: FlaskClient, test_user: dict) -> None:
    """Test viewing the cart."""
    client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })

    response = client.get('/cart')
    assert response.status_code == 200


def test_remove_from_cart(
    client: FlaskClient,
    test_user: dict,
    test_product: Cart
) -> None:
    """Test removing an item from cart."""
    # Login first
    client.post('/user/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })

    # Add item to cart
    client.post(f'/cart/add/{test_product.id}', json={'quantity': 1})

    # Then try to remove it
    response = client.delete(f'/cart/remove/{test_product.id}')
    assert response.status_code == 200
    assert b"Item removed from cart" in response.data
    assert Cart.query.count() == 0
