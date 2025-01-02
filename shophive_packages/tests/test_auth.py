# tests/test_auth.py
import pytest  # noqa
from shophive_packages import db
from shophive_packages.models import User


def test_user_registration(client):
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


def test_user_login(client):
    """
    Test user login functionality.

    Args:
        client (FlaskClient): The test client.

    Asserts:
        The response status code is 200 (OK).
        The response contains "Login successful" in the data.
    """
    user = User(username="existinguser", email="user@example.com",
                password="password")
    db.session.add(user)
    db.session.commit()
    response = client.post(
        "/login",
        json={
            "username": "existinguser",
            "email": "user@example.com",
            "password": "password",
        },
    )
    assert response.status_code == 200
    assert b"Logged in successfully!" in response.data
