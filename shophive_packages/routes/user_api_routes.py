from flask import Blueprint, jsonify, request, Response
from shophive_packages import db
from shophive_packages.models import User
from shophive_packages.db_utils import get_by_id

user_api_bp = Blueprint('user_api', __name__)


@user_api_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id: int) -> tuple[Response, int]:
    """Get user details"""
    user = get_by_id(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }), 200


@user_api_bp.route('/api/users', methods=['POST'])
def create_user() -> tuple[Response, int]:
    """Create new user"""
    data = request.get_json()

    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'User created successfully',
        'user': {
            'id': user.id,
            'username': user.username
        }
    }), 201
