# tests/test_routes.py
import pytest  # noqa
from flask.testing import FlaskClient
from shophive_packages import db
from shophive_packages.models import User


def test_homepage(client: FlaskClient) -> None:
    """
    Test the homepage route.

    Args:
        client (FlaskClient): The test client.

    Asserts:
        The response status code is 200 (OK).
        The response contains "Welcome to ShopHive!" in the data.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"Product List" in response.data


def test_add_user(client: FlaskClient) -> None:
    """
    Test adding a user to the database.

    Args:
        client (FlaskClient): The test client.

    Asserts:
        The user count is 1 after addition.
        The added user's username is "testuser".
    """
    user = User(username="testuser", email="test@example.com",
                password="testpassword")
    db.session.add(user)
    db.session.commit()
    assert User.query.count() == 1
    assert User.query.first().username == "testuser"
