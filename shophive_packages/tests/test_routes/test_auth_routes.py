from flask.testing import FlaskClient


def test_user_registration(client: FlaskClient) -> None:
    """Test user registration."""
    response = client.post('/user/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword',
        'role': 'buyer'
    })
    assert response.status_code == 302  # Redirect after registration success


def test_user_login(client: FlaskClient, test_user: dict) -> None:
    """Test user login."""
    response = client.post('/user/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 302  # Redirect after successful login


def test_invalid_login(client: FlaskClient) -> None:
    """Test login with invalid credentials."""
    response = client.post('/user/login', data={
        'username': 'wronguser',
        'password': 'wrongpass'
    })
    assert response.status_code == 401


def test_logout(client: FlaskClient, test_user: dict) -> None:
    """Test user logout."""
    # Login first
    client.post('/user/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })

    # Then logout
    response = client.get('/user/logout')
    assert response.status_code == 302  # Redirect after logout
