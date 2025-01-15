# tests/conftest.py
import pytest
from shophive_packages import create_app, db
from shophive_packages.models import User, Product
from typing import Generator
from flask.testing import FlaskClient
from flask import Flask


@pytest.fixture
def app() -> Flask:
    """Create and configure a test Flask application."""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test_secret_key'
    })
    return app


@pytest.fixture
def client(app: Flask) -> Generator[FlaskClient, None, None]:
    """Create a test client for the app."""
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create all tables before each test
            yield client
            db.session.remove()
            db.drop_all()  # Clean up after each test


@pytest.fixture
def test_user(client: FlaskClient) -> User:
    """Create a test user."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("testpass")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def test_product(client: FlaskClient) -> Product:
    """Create a test product."""
    product = Product(
        name="Test Product",
        description="Test Description",
        price=99.99
    )
    db.session.add(product)
    db.session.commit()
    return product
