# tests/conftest.py
import pytest
from app import app, db


@pytest.fixture
def client():
    """
    Fixture to set up a test client for the Flask application with a temporary
    database.

    Yields:
        FlaskClient: A test client for the Flask application.
    """
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()
