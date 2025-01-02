# tests/test_models/test_user_model.py
import pytest  # noqa
from shophive_packages import db
from shophive_packages.models import User


def test_user_model_repr():
    """
    Test the string representation of the User model.

    Asserts:
        The string representation matches the expected format.
    """
    user = User(username="testuser", email="test@example.com",
                password="testpassword")
    assert str(user) == "<User testuser>"


def test_user_unique_constraints(client):
    """
    Test the unique constraints on the User model's username and email.

    Args:
        client (FlaskClient): The test client.

    Asserts:
        An exception is raised when attempting to add a user with a duplicate
        username or email.
    """
    user1 = User(username="user1", email="user1@example.com", password="pass1")
    user2 = User(username="user1", email="user1@example.com", password="pass2")
    db.session.add(user1)
    db.session.commit()
    db.session.add(user2)
    with pytest.raises(Exception):
        db.session.commit()
