from flask_jwt_extended import create_access_token
from shophive_packages.models import User, Seller
from shophive_packages import db


# Register a new user
def register_user(
    username: str, email: str, password: str, role: str = "buyer"
) -> User:
    """Register a new user."""
    if User.query.filter_by(username=username).first():
        raise ValueError("Username already exists")
    if User.query.filter_by(email=email).first():
        raise ValueError("Email already exists")

    user = User(
        username=username,
        email=email,
        role=role
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


# User login: verify credentials and return user data with token
def login_user(username: str, password: str) -> dict[str, User | Seller | str]:
    """Login a user and return the user object with access token"""
    # Check User table first
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return {"user": user, "access_token": access_token}

    # If not found in User table, check Seller table
    seller = Seller.query.filter_by(username=username).first()
    if seller and seller.check_password(password):
        access_token = create_access_token(identity=seller.id)
        return {"user": seller, "access_token": access_token}

    raise ValueError("Invalid username or password.")
