from flask import testing
from shophive_packages import db
from shophive_packages.models import Product
from shophive_packages.db_utils import get_by_id


def test_pagination(client: testing.FlaskClient) -> None:
    """Test product pagination."""
    # Create multiple test products
    for i in range(15):
        product = Product(
            name=f"Product {i}",
            description=f"Description {i}",
            price=10.00 + i
        )
        db.session.add(product)
    db.session.commit()

    response = client.get('/products/page/1')
    assert response.status_code == 200
    assert b'Product 0' in response.data
    assert b'Product 9' in response.data  # Assuming 10 items per page


def test_update_product(client: testing.FlaskClient) -> None:
    """Test product update functionality."""
    # Create test product
    product = Product(
        name="Original Name",
        description="Original Description",
        price=10.00
    )
    db.session.add(product)
    db.session.commit()

    # Update product
    update_data = {
        'name': 'Updated Name',
        'description': 'Updated Description',
        'price': 20.00
    }
    response = client.post(
        f'/products/{product.id}/update',
        data=update_data,
        follow_redirects=True
    )
    assert response.status_code == 200

    updated_product = get_by_id(Product, product.id)
    assert updated_product is not None
    assert updated_product.name == 'Updated Name'
    assert updated_product.price == 20.00
