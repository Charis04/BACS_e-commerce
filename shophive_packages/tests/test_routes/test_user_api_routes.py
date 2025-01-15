import json
from flask.testing import FlaskClient
from shophive_packages import db
from shophive_packages.models import User


def test_get_user_api(client: FlaskClient) -> None:
    """Test GET request to user API."""
    # Create test user
    user = User(username="apiuser", email="api@test.com")
    user.set_password("testpass")
    db.session.add(user)
    db.session.commit()

    response = client.get('/api/users/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['username'] == 'apiuser'


def test_create_user_api(client: FlaskClient) -> None:
    """Test POST request to create user via API."""
    user_data = {
        'username': 'newuser',
        'email': 'new@test.com',
        'password': 'testpass'
    }
    response = client.post('/api/users',
                           data=json.dumps(user_data),
                           content_type='application/json')
    assert response.status_code == 201
    assert User.query.filter_by(username='newuser').first() is not None
