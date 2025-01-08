from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta
from shophive_packages.models import User
from shophive_packages import db

# Register a new user
def register_user(username, email, password, role):
    if User.query.filter_by(username=username).first():
        raise ValueError("Username already exists.")
    if User.query.filter_by(email=email).first():
        raise ValueError("Email already exists.")
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

# User login: verify credentials and return JWT
def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        raise ValueError("Invalid username or password.")
    token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))
    return token
