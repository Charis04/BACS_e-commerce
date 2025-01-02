# tests/test_homepage.py
import pytest  # noqa


def test_homepage(client):
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
    assert b"<h1>Product List</h1>" in response.data
