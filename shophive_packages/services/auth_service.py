from flask_jwt_extended import create_access_token
from shophive_packages.models import User
from shophive_packages import db


# Register a new user
def register_user(username: str, email: str, password: str, role: str) -> User:
    if User.query.filter_by(username=username).first():
        raise ValueError("Username already exists.")
    if User.query.filter_by(email=email).first():
        raise ValueError("Email already exists.")
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


# User login: verify credentials and return user data with token
def login_user(username: str, password: str) -> dict[str, User | str]:
    """Login a user and return the user object with access token"""
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        raise ValueError("Invalid username or password.")
    access_token = create_access_token(identity=user.id)
    return {"user": user, "access_token": access_token}
