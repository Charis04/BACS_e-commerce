# tests/test_auth.py
import pytest  # noqa
from flask.testing import FlaskClient
from shophive_packages import db
from shophive_packages.models import User


def test_user_registration(client: FlaskClient) -> None:
    """
    Test user registration functionality.

    Args:
        client (FlaskClient): The test client.

    Asserts:
        The response status code is 201 (Created).
        The user count is 1 after registration.
        The registered user's username is "newuser".
    """
    response = client.post(
        "/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
        },
    )
    assert response.status_code == 201
    assert User.query.count() == 1
    assert User.query.first().username == "newuser"


def test_user_login(client: FlaskClient) -> None:
    """Test user login functionality"""
    # Create a test user
    user = User(
        username="existinguser",
        email="user@example.com",
    )
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    # Attempt login
    response = client.post(
        "/user/login",  # Updated endpoint
        data={  # Changed from json to data
            "username": "existinguser",
            "password": "password",
        },
    )
    assert response.status_code == 302  # Redirect after successful login
