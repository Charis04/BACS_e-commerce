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

    # Verify user creation
    assert User.query.count() == 1
    user = User.query.first()
    assert user is not None  # Type guard
    assert user.username == "newuser"


def test_user_login(client: FlaskClient) -> None:
    """Test user login functionality"""
    # Create a test user
    test_user = User(
        username="existinguser",
        email="user@example.com",
    )
    test_user.set_password("password")
    db.session.add(test_user)
    db.session.commit()

    # Attempt login
    response = client.post(
        "/user/login",
        data={
            "username": "existinguser",
            "password": "password",
        },
    )
    assert response.status_code == 302  # Redirect after successful login
