from flask.testing import FlaskClient
from shophive_packages.models import Product


def test_create_product(client: FlaskClient, test_user: dict) -> None:
    """Test product creation."""
    client.post('/user/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    response = client.post('/add-product', data={
        'name': 'New Product',
        'description': 'Product Description',
        'price': '199.99'
    })
    assert response.status_code == 302
    assert Product.query.count() == 1


def test_update_product(client: FlaskClient, test_product: Product) -> None:
    """Test product update."""
    response = client.post(f'/update-product/{test_product.id}', data={
        'name': 'Updated Product',
        'description': 'Updated Description',
        'price': '299.99'
    })
    assert response.status_code == 302
    assert Product.query.first().name == 'Updated Product'


def test_delete_product(client: FlaskClient, test_product: Product) -> None:
    """Test product deletion."""
    response = client.post(f'/delete-product/{test_product.id}')
    assert response.status_code == 302
    assert Product.query.count() == 0


def test_view_product(client: FlaskClient, test_product: Product) -> None:
    """Test viewing a product."""
    response = client.get(f'/product/{test_product.id}')
    assert response.status_code == 200
    assert b'Test Product' in response.data
