# tests/test_models/test_user_model.py
import pytest  # noqa
from shophive_packages import db
from shophive_packages.models import User


def test_user_model_repr() -> None:
    """
    Test the string representation of the User model.

    Asserts:
        The string representation matches the expected format.
    """
    user = User(username="testuser", email="test@example.com",
                password="testpassword")
    assert str(user) == "<User testuser>"


def test_user_unique_constraints(client: pytest.FixtureRequest) -> None:
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


def test_user_creation(client: pytest.FixtureRequest) -> None:
    """Test user model creation."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    assert User.query.count() == 1
    user_result = User.query.first()
    assert user_result is not None
    retrieved_user: User = user_result
    assert retrieved_user.username == "testuser"
    assert retrieved_user.check_password("password123")


def test_user_password_hashing(client: pytest.FixtureRequest) -> None:
    """Test password hashing."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")

    assert user.password != "password123"
    assert user.check_password("password123")
    assert not user.check_password("wrongpassword")


def test_user_repr(client: pytest.FixtureRequest) -> None:
    """Test string representation of user."""
    user = User(username="testuser", email="test@example.com")
    assert str(user) == "<User testuser>"
